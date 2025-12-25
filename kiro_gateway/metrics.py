# -*- coding: utf-8 -*-

# KiroGate
# Based on kiro-openai-gateway by Jwadow (https://github.com/Jwadow/kiro-openai-gateway)
# Original Copyright (C) 2025 Jwadow
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Prometheus metrics module.

Provides structured application metrics collection and export.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from threading import Lock

from loguru import logger

from kiro_gateway.config import APP_VERSION


@dataclass
class MetricsBucket:
    """Metrics bucket for histogram data."""
    le: float  # Upper bound
    count: int = 0


class PrometheusMetrics:
    """
    Prometheus-style metrics collector.

    Collects the following metrics:
    - Total requests (by endpoint, status code, model)
    - Request latency histogram
    - Token usage (input/output)
    - Retry count
    - Active connections
    - Error count
    """

    # Latency histogram bucket boundaries (seconds)
    LATENCY_BUCKETS = [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')]

    def __init__(self):
        """Initialize metrics collector."""
        self._lock = Lock()

        # Counters
        self._request_total: Dict[str, int] = defaultdict(int)  # {endpoint:status:model: count}
        self._error_total: Dict[str, int] = defaultdict(int)  # {error_type: count}
        self._retry_total: Dict[str, int] = defaultdict(int)  # {endpoint: count}

        # Token counters
        self._input_tokens_total: Dict[str, int] = defaultdict(int)  # {model: tokens}
        self._output_tokens_total: Dict[str, int] = defaultdict(int)  # {model: tokens}

        # Histograms
        self._latency_histogram: Dict[str, List[int]] = defaultdict(
            lambda: [0] * len(self.LATENCY_BUCKETS)
        )  # {endpoint: [bucket_counts]}
        self._latency_sum: Dict[str, float] = defaultdict(float)  # {endpoint: sum}
        self._latency_count: Dict[str, int] = defaultdict(int)  # {endpoint: count}

        # Gauges
        self._active_connections = 0
        self._cache_size = 0
        self._token_valid = False

        # Start time
        self._start_time = time.time()

    def inc_request(self, endpoint: str, status_code: int, model: str = "unknown") -> None:
        """
        Increment request count.

        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            model: Model name
        """
        with self._lock:
            key = f"{endpoint}:{status_code}:{model}"
            self._request_total[key] += 1

    def inc_error(self, error_type: str) -> None:
        """
        Increment error count.

        Args:
            error_type: Error type
        """
        with self._lock:
            self._error_total[error_type] += 1

    def inc_retry(self, endpoint: str) -> None:
        """
        Increment retry count.

        Args:
            endpoint: API endpoint
        """
        with self._lock:
            self._retry_total[endpoint] += 1

    def observe_latency(self, endpoint: str, latency: float) -> None:
        """
        Record request latency.

        Args:
            endpoint: API endpoint
            latency: Latency in seconds
        """
        with self._lock:
            # Update histogram buckets
            for i, le in enumerate(self.LATENCY_BUCKETS):
                if latency <= le:
                    self._latency_histogram[endpoint][i] += 1

            # Update sum and count
            self._latency_sum[endpoint] += latency
            self._latency_count[endpoint] += 1

    def add_tokens(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """
        Add token usage.

        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
        """
        with self._lock:
            self._input_tokens_total[model] += input_tokens
            self._output_tokens_total[model] += output_tokens

    def set_active_connections(self, count: int) -> None:
        """Set active connection count."""
        with self._lock:
            self._active_connections = count

    def inc_active_connections(self) -> None:
        """Increment active connection count."""
        with self._lock:
            self._active_connections += 1

    def dec_active_connections(self) -> None:
        """Decrement active connection count."""
        with self._lock:
            self._active_connections = max(0, self._active_connections - 1)

    def set_cache_size(self, size: int) -> None:
        """Set cache size."""
        with self._lock:
            self._cache_size = size

    def set_token_valid(self, valid: bool) -> None:
        """Set token validity status."""
        with self._lock:
            self._token_valid = valid

    def get_metrics(self) -> Dict:
        """
        Get all metrics.

        Returns:
            Metrics dictionary
        """
        with self._lock:
            # Calculate average latency and percentiles
            latency_stats = {}
            for endpoint, counts in self._latency_histogram.items():
                total_count = self._latency_count[endpoint]
                if total_count > 0:
                    avg = self._latency_sum[endpoint] / total_count

                    # Calculate P50, P95, P99
                    p50 = self._calculate_percentile(counts, total_count, 0.50)
                    p95 = self._calculate_percentile(counts, total_count, 0.95)
                    p99 = self._calculate_percentile(counts, total_count, 0.99)

                    latency_stats[endpoint] = {
                        "avg": round(avg, 4),
                        "p50": round(p50, 4),
                        "p95": round(p95, 4),
                        "p99": round(p99, 4),
                        "count": total_count
                    }

            return {
                "version": APP_VERSION,
                "uptime_seconds": round(time.time() - self._start_time, 2),
                "requests": {
                    "total": dict(self._request_total),
                    "by_endpoint": self._aggregate_by_endpoint(),
                    "by_status": self._aggregate_by_status(),
                    "by_model": self._aggregate_by_model()
                },
                "errors": dict(self._error_total),
                "retries": dict(self._retry_total),
                "latency": latency_stats,
                "tokens": {
                    "input": dict(self._input_tokens_total),
                    "output": dict(self._output_tokens_total),
                    "total_input": sum(self._input_tokens_total.values()),
                    "total_output": sum(self._output_tokens_total.values())
                },
                "gauges": {
                    "active_connections": self._active_connections,
                    "cache_size": self._cache_size,
                    "token_valid": self._token_valid
                }
            }

    def _calculate_percentile(self, bucket_counts: List[int], total: int, percentile: float) -> float:
        """
        Calculate percentile from histogram buckets.

        Args:
            bucket_counts: Bucket count list
            total: Total count
            percentile: Percentile (0-1)

        Returns:
            Estimated percentile value
        """
        if total == 0:
            return 0.0

        target = total * percentile
        cumulative = 0

        for i, count in enumerate(bucket_counts):
            cumulative += count
            if cumulative >= target:
                # Return bucket upper bound as estimate
                return self.LATENCY_BUCKETS[i] if self.LATENCY_BUCKETS[i] != float('inf') else 120.0

        return self.LATENCY_BUCKETS[-2]  # Return last finite bucket

    def _aggregate_by_endpoint(self) -> Dict[str, int]:
        """Aggregate request count by endpoint."""
        result = defaultdict(int)
        for key, count in self._request_total.items():
            endpoint = key.split(":")[0]
            result[endpoint] += count
        return dict(result)

    def _aggregate_by_status(self) -> Dict[str, int]:
        """Aggregate request count by status code."""
        result = defaultdict(int)
        for key, count in self._request_total.items():
            status = key.split(":")[1]
            result[status] += count
        return dict(result)

    def _aggregate_by_model(self) -> Dict[str, int]:
        """Aggregate request count by model."""
        result = defaultdict(int)
        for key, count in self._request_total.items():
            parts = key.split(":")
            if len(parts) >= 3:
                model = parts[2]
                result[model] += count
        return dict(result)

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus text format metrics
        """
        lines = []

        with self._lock:
            # Info metric with version
            lines.append("# HELP kirogate_info KiroGate version information")
            lines.append("# TYPE kirogate_info gauge")
            lines.append(f'kirogate_info{{version="{APP_VERSION}"}} 1')

            # Total requests
            lines.append("# HELP kirogate_requests_total Total number of requests")
            lines.append("# TYPE kirogate_requests_total counter")
            for key, count in self._request_total.items():
                parts = key.split(":")
                endpoint, status, model = parts[0], parts[1], parts[2] if len(parts) > 2 else "unknown"
                lines.append(
                    f'kirogate_requests_total{{endpoint="{endpoint}",status="{status}",model="{model}"}} {count}'
                )

            # Total errors
            lines.append("# HELP kirogate_errors_total Total number of errors")
            lines.append("# TYPE kirogate_errors_total counter")
            for error_type, count in self._error_total.items():
                lines.append(f'kirogate_errors_total{{type="{error_type}"}} {count}')

            # Total retries
            lines.append("# HELP kirogate_retries_total Total number of retries")
            lines.append("# TYPE kirogate_retries_total counter")
            for endpoint, count in self._retry_total.items():
                lines.append(f'kirogate_retries_total{{endpoint="{endpoint}"}} {count}')

            # Token usage
            lines.append("# HELP kirogate_tokens_total Total tokens used")
            lines.append("# TYPE kirogate_tokens_total counter")
            for model, tokens in self._input_tokens_total.items():
                lines.append(f'kirogate_tokens_total{{model="{model}",type="input"}} {tokens}')
            for model, tokens in self._output_tokens_total.items():
                lines.append(f'kirogate_tokens_total{{model="{model}",type="output"}} {tokens}')

            # Latency histogram
            lines.append("# HELP kirogate_request_duration_seconds Request duration histogram")
            lines.append("# TYPE kirogate_request_duration_seconds histogram")
            for endpoint, counts in self._latency_histogram.items():
                cumulative = 0
                for i, count in enumerate(counts):
                    cumulative += count
                    le = self.LATENCY_BUCKETS[i]
                    le_str = "+Inf" if le == float('inf') else str(le)
                    lines.append(
                        f'kirogate_request_duration_seconds_bucket{{endpoint="{endpoint}",le="{le_str}"}} {cumulative}'
                    )
                lines.append(
                    f'kirogate_request_duration_seconds_sum{{endpoint="{endpoint}"}} {self._latency_sum[endpoint]}'
                )
                lines.append(
                    f'kirogate_request_duration_seconds_count{{endpoint="{endpoint}"}} {self._latency_count[endpoint]}'
                )

            # Gauges
            lines.append("# HELP kirogate_active_connections Current active connections")
            lines.append("# TYPE kirogate_active_connections gauge")
            lines.append(f"kirogate_active_connections {self._active_connections}")

            lines.append("# HELP kirogate_cache_size Current cache size")
            lines.append("# TYPE kirogate_cache_size gauge")
            lines.append(f"kirogate_cache_size {self._cache_size}")

            lines.append("# HELP kirogate_token_valid Token validity status")
            lines.append("# TYPE kirogate_token_valid gauge")
            lines.append(f"kirogate_token_valid {1 if self._token_valid else 0}")

            lines.append("# HELP kirogate_uptime_seconds Uptime in seconds")
            lines.append("# TYPE kirogate_uptime_seconds gauge")
            lines.append(f"kirogate_uptime_seconds {round(time.time() - self._start_time, 2)}")

        return "\n".join(lines) + "\n"


# Global metrics instance
metrics = PrometheusMetrics()
