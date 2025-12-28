# -*- coding: utf-8 -*-

"""
KiroGate 智能 Token 分配器。

实现基于成功率、新鲜度和负载均衡的 Token 智能分配算法。
"""

import time
from typing import Optional, Tuple

from loguru import logger

from kiro_gateway.database import user_db, DonatedToken
from kiro_gateway.auth import KiroAuthManager
from kiro_gateway.config import settings


class NoTokenAvailable(Exception):
    """No active token available for allocation."""
    pass


class SmartTokenAllocator:
    """智能 Token 分配器。"""

    def __init__(self):
        self._token_managers: dict[int, KiroAuthManager] = {}

    def calculate_score(self, token: DonatedToken) -> float:
        """
        计算 Token 评分 (0-100)。

        评分基于：
        - 成功率 (权重 60%)
        - 新鲜度 (权重 20%)
        - 负载均衡 (权重 20%)
        """
        now = int(time.time() * 1000)

        # 基础分: 成功率 (权重60%)
        total = token.success_count + token.fail_count
        if total == 0:
            success_rate = 1.0  # 新Token给予高分
        else:
            success_rate = token.success_count / total

        # 如果成功率低于阈值，大幅降分
        if success_rate < settings.token_min_success_rate and total > 10:
            base_score = success_rate * 30  # 降低权重
        else:
            base_score = success_rate * 60

        # 新鲜度: 最近使用时间 (权重20%)
        if token.last_used:
            hours_since_use = (now - token.last_used) / 3600000
        else:
            hours_since_use = 0  # 从未使用，视为新鲜

        if hours_since_use < 1:
            freshness = 20
        elif hours_since_use < 24:
            freshness = 15
        else:
            freshness = max(5, 20 - hours_since_use / 24)

        # 负载均衡: 使用频率 (权重20%)
        # 使用次数少的Token优先，避免单个Token过载
        usage_score = max(0, 20 - (total / 100))

        return base_score + freshness + usage_score

    async def get_best_token(self, user_id: Optional[int] = None) -> Tuple[DonatedToken, KiroAuthManager]:
        """
        获取最优 Token。

        对于有用户的请求，优先使用用户自己的私有 Token。
        否则使用公共 Token 池。

        Returns:
            (DonatedToken, KiroAuthManager) tuple

        Raises:
            NoTokenAvailable: 无可用 Token
        """
        from kiro_gateway.metrics import metrics
        self_use_enabled = metrics.is_self_use_enabled()

        if user_id:
            # 用户请求: 优先使用用户自己的私有 Token
            user_tokens = user_db.get_user_tokens(user_id)
            active_tokens = [
                t for t in user_tokens
                if t.status == "active" and (not self_use_enabled or t.visibility == "private")
            ]
            if active_tokens:
                best = max(active_tokens, key=self.calculate_score)
                manager = await self._get_manager(best)
                return best, manager

        if self_use_enabled:
            raise NoTokenAvailable("Self-use mode: public token pool is disabled")

        # 使用公共 Token 池
        public_tokens = user_db.get_public_tokens()
        if not public_tokens:
            raise NoTokenAvailable("No public tokens available")

        # 过滤掉低成功率的 Token
        good_tokens = [
            t for t in public_tokens
            if t.success_rate >= settings.token_min_success_rate or
               (t.success_count + t.fail_count) < 10  # 给新Token机会
        ]

        if not good_tokens:
            # 如果没有好的Token，使用所有可用的
            good_tokens = public_tokens

        best = max(good_tokens, key=self.calculate_score)
        manager = await self._get_manager(best)
        return best, manager

    async def _get_manager(self, token: DonatedToken) -> KiroAuthManager:
        """获取或创建 Token 对应的 AuthManager。"""
        if token.id in self._token_managers:
            return self._token_managers[token.id]

        # 获取解密的 refresh token
        refresh_token = user_db.get_decrypted_token(token.id)
        if not refresh_token:
            raise NoTokenAvailable(f"Failed to decrypt token {token.id}")

        manager = KiroAuthManager(
            refresh_token=refresh_token,
            region=settings.region,
            profile_arn=settings.profile_arn
        )

        self._token_managers[token.id] = manager
        return manager

    def record_usage(self, token_id: int, success: bool) -> None:
        """记录 Token 使用结果。"""
        user_db.record_token_usage(token_id, success)

    def clear_manager(self, token_id: int) -> None:
        """清除缓存的 AuthManager。"""
        if token_id in self._token_managers:
            del self._token_managers[token_id]


# Global allocator instance
token_allocator = SmartTokenAllocator()
