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

import os
import sqlite3
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from dataclasses import dataclass
from threading import Lock

from loguru import logger

from kiro_gateway.config import APP_VERSION

METRICS_DB_FILE = os.getenv("METRICS_DB_FILE", "data/metrics.db")


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
    MAX_RECENT_REQUESTS = 50
    MAX_RESPONSE_TIMES = 100

    def __init__(self):
        """Initialize metrics collector."""
        self._lock = Lock()
        self._db_path = METRICS_DB_FILE
        self._init_db()

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

        # Deno-compatible fields
        self._stream_requests = 0
        self._non_stream_requests = 0
        self._response_times: List[float] = []
        self._recent_requests: List[Dict] = []
        self._api_type_usage: Dict[str, int] = defaultdict(int)  # {openai/anthropic: count}
        self._hourly_requests: Dict[int, int] = defaultdict(int)  # {hour_timestamp: count}

        # IP statistics and blacklist
        self._ip_requests: Dict[str, int] = defaultdict(int)  # {ip: count}
        self._ip_last_seen: Dict[str, int] = {}  # {ip: timestamp_ms}
        self._ip_blacklist: Dict[str, Dict] = {}  # {ip: {banned_at, reason}}
        self._site_enabled: bool = True  # Site on/off switch

        # Load persisted data
        self._load_from_db()

    def _init_db(self) -> None:
        """Initialize SQLite database and create tables."""
        os.makedirs(os.path.dirname(self._db_path) or ".", exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS counters (
                    key TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS hourly_requests (
                    hour_ts INTEGER PRIMARY KEY,
                    count INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS recent_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    api_type TEXT,
                    path TEXT,
                    status INTEGER,
                    duration REAL,
                    model TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_recent_ts ON recent_requests(timestamp);
                CREATE TABLE IF NOT EXISTS ip_stats (
                    ip TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    last_seen INTEGER
                );
                CREATE TABLE IF NOT EXISTS ip_blacklist (
                    ip TEXT PRIMARY KEY,
                    banned_at INTEGER,
                    reason TEXT
                );
                CREATE TABLE IF NOT EXISTS site_config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            ''')
            conn.commit()

    def _load_from_db(self) -> None:
        """Load metrics from SQLite database."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                # Load counters
                cursor = conn.execute("SELECT key, value FROM counters")
                for key, value in cursor:
                    if key.startswith("req:"):
                        self._request_total[key[4:]] = value
                    elif key.startswith("err:"):
                        self._error_total[key[4:]] = value
                    elif key.startswith("retry:"):
                        self._retry_total[key[6:]] = value
                    elif key.startswith("api:"):
                        self._api_type_usage[key[4:]] = value
                    elif key.startswith("in_tok:"):
                        self._input_tokens_total[key[7:]] = value
                    elif key.startswith("out_tok:"):
                        self._output_tokens_total[key[8:]] = value
                    elif key == "stream_requests":
                        self._stream_requests = value
                    elif key == "non_stream_requests":
                        self._non_stream_requests = value

                # Load hourly requests
                cursor = conn.execute("SELECT hour_ts, count FROM hourly_requests")
                for hour_ts, count in cursor:
                    self._hourly_requests[hour_ts] = count

                # Load recent requests (last 50)
                cursor = conn.execute(
                    "SELECT timestamp, api_type, path, status, duration, model "
                    "FROM recent_requests ORDER BY id DESC LIMIT 50"
                )
                rows = cursor.fetchall()
                self._recent_requests = [
                    {"timestamp": r[0], "apiType": r[1], "path": r[2],
                     "status": r[3], "duration": r[4], "model": r[5]}
                    for r in reversed(rows)
                ]

                # Load IP stats
                cursor = conn.execute("SELECT ip, count, last_seen FROM ip_stats")
                for ip, count, last_seen in cursor:
                    self._ip_requests[ip] = count
                    self._ip_last_seen[ip] = last_seen

                # Load IP blacklist
                cursor = conn.execute("SELECT ip, banned_at, reason FROM ip_blacklist")
                for ip, banned_at, reason in cursor:
                    self._ip_blacklist[ip] = {"banned_at": banned_at, "reason": reason}

                # Load site config
                cursor = conn.execute("SELECT key, value FROM site_config WHERE key = 'site_enabled'")
                row = cursor.fetchone()
                if row:
                    self._site_enabled = row[1] == "true"

                logger.info(f"Loaded metrics from {self._db_path}")
        except Exception as e:
            logger.warning(f"Failed to load metrics from DB: {e}")

    def _save_counter(self, key: str, value: int) -> None:
        """Save a single counter to database."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO counters (key, value) VALUES (?, ?)",
                    (key, value)
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"Failed to save counter: {e}")

    def _save_hourly(self, hour_ts: int, count: int) -> None:
        """Save hourly request count."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO hourly_requests (hour_ts, count) VALUES (?, ?)",
                    (hour_ts, count)
                )
                # Clean old data (> 24h)
                cutoff = hour_ts - 24 * 3600000
                conn.execute("DELETE FROM hourly_requests WHERE hour_ts < ?", (cutoff,))
                conn.commit()
        except Exception as e:
            logger.debug(f"Failed to save hourly: {e}")

    def _save_recent_request(self, req: Dict) -> None:
        """Save a recent request to database."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO recent_requests (timestamp, api_type, path, status, duration, model) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (req["timestamp"], req["apiType"], req["path"],
                     req["status"], req["duration"], req["model"])
                )
                # Keep only last 100 records
                conn.execute(
                    "DELETE FROM recent_requests WHERE id NOT IN "
                    "(SELECT id FROM recent_requests ORDER BY id DESC LIMIT 100)"
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"Failed to save recent request: {e}")

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
            self._save_counter(f"req:{key}", self._request_total[key])

    def inc_error(self, error_type: str) -> None:
        """
        Increment error count.

        Args:
            error_type: Error type
        """
        with self._lock:
            self._error_total[error_type] += 1
            self._save_counter(f"err:{error_type}", self._error_total[error_type])

    def inc_retry(self, endpoint: str) -> None:
        """
        Increment retry count.

        Args:
            endpoint: API endpoint
        """
        with self._lock:
            self._retry_total[endpoint] += 1
            self._save_counter(f"retry:{endpoint}", self._retry_total[endpoint])

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
            self._save_counter(f"in_tok:{model}", self._input_tokens_total[model])
            self._save_counter(f"out_tok:{model}", self._output_tokens_total[model])

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

    def record_request(
        self,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        model: str = "unknown",
        is_stream: bool = False,
        api_type: str = "openai"
    ) -> None:
        """
        Record a complete request with all Deno-compatible fields.

        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            duration_ms: Duration in milliseconds
            model: Model name
            is_stream: Whether streaming request
            api_type: API type (openai/anthropic)
        """
        with self._lock:
            # Increment stream/non-stream counters
            if is_stream:
                self._stream_requests += 1
                self._save_counter("stream_requests", self._stream_requests)
            else:
                self._non_stream_requests += 1
                self._save_counter("non_stream_requests", self._non_stream_requests)

            # Track API type usage
            self._api_type_usage[api_type] += 1
            self._save_counter(f"api:{api_type}", self._api_type_usage[api_type])

            # Add to response times (keep last N)
            self._response_times.append(duration_ms)
            if len(self._response_times) > self.MAX_RESPONSE_TIMES:
                self._response_times.pop(0)

            # Add to recent requests (keep last N)
            now = int(time.time() * 1000)
            req = {
                "timestamp": now,
                "apiType": api_type,
                "path": endpoint,
                "status": status_code,
                "duration": duration_ms,
                "model": model
            }
            self._recent_requests.append(req)
            if len(self._recent_requests) > self.MAX_RECENT_REQUESTS:
                self._recent_requests.pop(0)
            self._save_recent_request(req)

            # Track hourly requests
            hour_ts = (now // 3600000) * 3600000
            self._hourly_requests[hour_ts] += 1
            self._save_hourly(hour_ts, self._hourly_requests[hour_ts])
            # Clean up old hourly data (keep only last 24 hours)
            cutoff = hour_ts - 24 * 3600000
            self._hourly_requests = defaultdict(
                int,
                {k: v for k, v in self._hourly_requests.items() if k >= cutoff}
            )

    def get_deno_compatible_metrics(self) -> Dict:
        """
        Get metrics in Deno-compatible format for dashboard.

        Returns:
            Deno-compatible metrics dictionary
        """
        with self._lock:
            # Calculate totals from request_total
            total_requests = sum(self._request_total.values())
            success_requests = 0
            failed_requests = 0

            for key, count in self._request_total.items():
                parts = key.split(":")
                if len(parts) >= 2:
                    status = int(parts[1])
                    if 200 <= status < 400:
                        success_requests += count
                    else:
                        failed_requests += count

            # Calculate average response time
            avg_response_time = 0.0
            if self._response_times:
                avg_response_time = sum(self._response_times) / len(self._response_times)

            # Aggregate model usage from recent requests (more accurate)
            model_usage = {}
            for req in self._recent_requests:
                model = req.get("model", "unknown")
                if model and model != "unknown":
                    model_usage[model] = model_usage.get(model, 0) + 1
            # Fallback to _request_total if no recent requests
            if not model_usage:
                for key, count in self._request_total.items():
                    parts = key.split(":")
                    if len(parts) >= 3:
                        model = parts[2]
                        if model != "unknown":
                            model_usage[model] = model_usage.get(model, 0) + count

            # Build 24-hour request data
            now = int(time.time() * 1000)
            current_hour = (now // 3600000) * 3600000
            hourly_data = []
            for i in range(24):
                hour_ts = current_hour - (23 - i) * 3600000
                hourly_data.append({
                    "hour": hour_ts,
                    "count": self._hourly_requests.get(hour_ts, 0)
                })

            return {
                "totalRequests": total_requests,
                "successRequests": success_requests,
                "failedRequests": failed_requests,
                "avgResponseTime": avg_response_time,
                "responseTimes": list(self._response_times),
                "streamRequests": self._stream_requests,
                "nonStreamRequests": self._non_stream_requests,
                "modelUsage": model_usage,
                "apiTypeUsage": dict(self._api_type_usage),
                "recentRequests": list(self._recent_requests),
                "startTime": int(self._start_time * 1000),
                "hourlyRequests": hourly_data
            }

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

    # ==================== IP Statistics & Admin Methods ====================

    def record_ip(self, ip: str) -> None:
        """Record IP request."""
        if not ip:
            return
        with self._lock:
            self._ip_requests[ip] += 1
            now = int(time.time() * 1000)
            self._ip_last_seen[ip] = now
            # Save to DB
            try:
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO ip_stats (ip, count, last_seen) VALUES (?, ?, ?)",
                        (ip, self._ip_requests[ip], now)
                    )
                    conn.commit()
            except Exception as e:
                logger.debug(f"Failed to save IP stats: {e}")

    def get_ip_stats(
        self,
        limit: int = 100,
        offset: int = 0,
        search: str = "",
        sort_field: str = "count",
        sort_order: str = "desc"
    ) -> Tuple[List[Dict], int]:
        """Get IP statistics sorted by request count with pagination."""
        with self._lock:
            stats = [
                {"ip": ip, "count": count, "lastSeen": self._ip_last_seen.get(ip, 0)}
                for ip, count in self._ip_requests.items()
            ]
            if search:
                stats = [item for item in stats if search in item["ip"]]
            sort_map = {"count": "count", "last_seen": "lastSeen", "ip": "ip"}
            key_name = sort_map.get(sort_field, "count")
            reverse = sort_order.lower() != "asc"
            stats.sort(key=lambda x: x.get(key_name, 0), reverse=reverse)
            total = len(stats)
            return stats[offset:offset + limit], total

    def is_ip_banned(self, ip: str) -> bool:
        """Check if IP is banned."""
        with self._lock:
            return ip in self._ip_blacklist

    def ban_ip(self, ip: str, reason: str = "") -> bool:
        """Ban an IP address."""
        if not ip:
            return False
        with self._lock:
            now = int(time.time() * 1000)
            self._ip_blacklist[ip] = {"banned_at": now, "reason": reason}
            try:
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO ip_blacklist (ip, banned_at, reason) VALUES (?, ?, ?)",
                        (ip, now, reason)
                    )
                    conn.commit()
                logger.info(f"Banned IP: {ip}, reason: {reason}")
                return True
            except Exception as e:
                logger.error(f"Failed to ban IP: {e}")
                return False

    def unban_ip(self, ip: str) -> bool:
        """Unban an IP address."""
        if not ip:
            return False
        with self._lock:
            if ip in self._ip_blacklist:
                del self._ip_blacklist[ip]
            try:
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute("DELETE FROM ip_blacklist WHERE ip = ?", (ip,))
                    conn.commit()
                logger.info(f"Unbanned IP: {ip}")
                return True
            except Exception as e:
                logger.error(f"Failed to unban IP: {e}")
                return False

    def get_blacklist(
        self,
        limit: int = 100,
        offset: int = 0,
        search: str = "",
        sort_field: str = "banned_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Dict], int]:
        """Get IP blacklist with pagination."""
        with self._lock:
            items = [
                {"ip": ip, "bannedAt": info["banned_at"], "reason": info["reason"]}
                for ip, info in self._ip_blacklist.items()
            ]
            if search:
                items = [
                    item for item in items
                    if search in item["ip"] or search in (item["reason"] or "")
                ]
            sort_map = {"banned_at": "bannedAt", "ip": "ip"}
            key_name = sort_map.get(sort_field, "bannedAt")
            reverse = sort_order.lower() != "asc"
            items.sort(key=lambda x: x.get(key_name, 0), reverse=reverse)
            total = len(items)
            return items[offset:offset + limit], total

    def is_site_enabled(self) -> bool:
        """Check if site is enabled."""
        with self._lock:
            return self._site_enabled

    def set_site_enabled(self, enabled: bool) -> bool:
        """Enable or disable site."""
        with self._lock:
            self._site_enabled = enabled
            try:
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO site_config (key, value) VALUES (?, ?)",
                        ("site_enabled", "true" if enabled else "false")
                    )
                    conn.commit()
                logger.info(f"Site enabled: {enabled}")
                return True
            except Exception as e:
                logger.error(f"Failed to set site status: {e}")
                return False

    def get_admin_stats(self) -> Dict:
        """Get statistics for admin dashboard."""
        with self._lock:
            total_requests = sum(self._request_total.values())
            success_requests = sum(
                c for k, c in self._request_total.items()
                if len(k.split(":")) >= 2 and 200 <= int(k.split(":")[1]) < 400
            )
            return {
                "totalRequests": total_requests,
                "successRequests": success_requests,
                "failedRequests": total_requests - success_requests,
                "streamRequests": self._stream_requests,
                "nonStreamRequests": self._non_stream_requests,
                "activeConnections": self._active_connections,
                "tokenValid": self._token_valid,
                "siteEnabled": self._site_enabled,
                "uptimeSeconds": round(time.time() - self._start_time, 2),
                "totalIPs": len(self._ip_requests),
                "bannedIPs": len(self._ip_blacklist),
            }


# Global metrics instance
metrics = PrometheusMetrics()
