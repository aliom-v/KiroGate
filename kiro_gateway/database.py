# -*- coding: utf-8 -*-

"""
KiroGate 用户系统数据库模块。

管理用户、Token、API Key 等数据的 SQLite 存储。
"""

import hashlib
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from typing import Dict, List, Optional, Tuple

from cryptography.fernet import Fernet
from loguru import logger

from kiro_gateway.config import settings

# Database file path
USER_DB_FILE = os.getenv("USER_DB_FILE", "data/users.db")


def _derive_key(secret: str) -> bytes:
    """Derive a Fernet-compatible key from secret string."""
    return hashlib.sha256(secret.encode()).digest()[:32]


def _get_fernet() -> Fernet:
    """Get Fernet instance for token encryption."""
    import base64
    key = _derive_key(settings.token_encrypt_key)
    return Fernet(base64.urlsafe_b64encode(key))


@dataclass
class User:
    """User data model."""
    id: int
    linuxdo_id: Optional[str]
    github_id: Optional[str]
    username: str
    avatar_url: Optional[str]
    trust_level: int
    is_admin: bool
    is_banned: bool
    created_at: int
    last_login: Optional[int]


@dataclass
class DonatedToken:
    """Donated token data model."""
    id: int
    user_id: int
    token_hash: str
    visibility: str  # 'public' or 'private'
    status: str  # 'active', 'invalid', 'expired'
    success_count: int
    fail_count: int
    last_used: Optional[int]
    last_check: Optional[int]
    created_at: int

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 1.0


@dataclass
class APIKey:
    """API Key data model."""
    id: int
    user_id: int
    key_prefix: str
    name: Optional[str]
    is_active: bool
    request_count: int
    last_used: Optional[int]
    created_at: int


class UserDatabase:
    """User system database manager."""

    def __init__(self):
        self._lock = Lock()
        self._db_path = USER_DB_FILE
        self._fernet = _get_fernet()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        os.makedirs(os.path.dirname(self._db_path) or ".", exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript('''
                -- Users table
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    linuxdo_id TEXT,
                    github_id TEXT,
                    username TEXT NOT NULL,
                    avatar_url TEXT,
                    trust_level INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    created_at INTEGER NOT NULL,
                    last_login INTEGER
                );
                CREATE INDEX IF NOT EXISTS idx_users_linuxdo ON users(linuxdo_id);
                CREATE INDEX IF NOT EXISTS idx_users_github ON users(github_id);

                -- Donated tokens table
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    refresh_token_encrypted TEXT NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    visibility TEXT DEFAULT 'private',
                    status TEXT DEFAULT 'active',
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    last_used INTEGER,
                    last_check INTEGER,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_tokens_user ON tokens(user_id);
                CREATE INDEX IF NOT EXISTS idx_tokens_visibility ON tokens(visibility, status);
                CREATE INDEX IF NOT EXISTS idx_tokens_hash ON tokens(token_hash);

                -- API Keys table
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    key_prefix TEXT NOT NULL,
                    name TEXT,
                    is_active INTEGER DEFAULT 1,
                    request_count INTEGER DEFAULT 0,
                    last_used INTEGER,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_apikeys_user ON api_keys(user_id);
                CREATE INDEX IF NOT EXISTS idx_apikeys_hash ON api_keys(key_hash);

                -- Token health check logs
                CREATE TABLE IF NOT EXISTS token_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_id INTEGER NOT NULL,
                    check_time INTEGER NOT NULL,
                    is_valid INTEGER NOT NULL,
                    error_msg TEXT,
                    FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_health_token ON token_health(token_id);
            ''')
            conn.commit()
        logger.info(f"User database initialized: {self._db_path}")

    @contextmanager
    def _get_conn(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ==================== User Methods ====================

    def create_user(
        self,
        username: str,
        linuxdo_id: Optional[str] = None,
        github_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        trust_level: int = 0
    ) -> User:
        """Create a new user."""
        if not linuxdo_id and not github_id:
            raise ValueError("必须提供 linuxdo_id 或 github_id")

        now = int(time.time() * 1000)
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    """INSERT INTO users (linuxdo_id, github_id, username, avatar_url, trust_level, created_at, last_login)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (linuxdo_id, github_id, username, avatar_url, trust_level, now, now)
                )
                user_id = cursor.lastrowid
                return User(
                    id=user_id,
                    linuxdo_id=linuxdo_id,
                    github_id=github_id,
                    username=username,
                    avatar_url=avatar_url,
                    trust_level=trust_level,
                    is_admin=False,
                    is_banned=False,
                    created_at=now,
                    last_login=now
                )

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_linuxdo(self, linuxdo_id: str) -> Optional[User]:
        """Get user by LinuxDo ID."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE linuxdo_id = ?", (linuxdo_id,)).fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_github(self, github_id: str) -> Optional[User]:
        """Get user by GitHub ID."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE github_id = ?", (github_id,)).fetchone()
            return self._row_to_user(row) if row else None

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login time."""
        now = int(time.time() * 1000)
        with self._lock:
            with self._get_conn() as conn:
                conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))

    def set_user_admin(self, user_id: int, is_admin: bool) -> None:
        """Set user admin status."""
        with self._lock:
            with self._get_conn() as conn:
                conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (1 if is_admin else 0, user_id))

    def set_user_banned(self, user_id: int, is_banned: bool) -> None:
        """Set user banned status."""
        with self._lock:
            with self._get_conn() as conn:
                conn.execute("UPDATE users SET is_banned = ? WHERE id = ?", (1 if is_banned else 0, user_id))

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
            return [self._row_to_user(r) for r in rows]

    def get_user_count(self) -> int:
        """Get total user count."""
        with self._get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert database row to User object."""
        return User(
            id=row["id"],
            linuxdo_id=row["linuxdo_id"],
            github_id=row["github_id"],
            username=row["username"],
            avatar_url=row["avatar_url"],
            trust_level=row["trust_level"],
            is_admin=bool(row["is_admin"]),
            is_banned=bool(row["is_banned"]),
            created_at=row["created_at"],
            last_login=row["last_login"]
        )

    # ==================== Token Methods ====================

    def _hash_token(self, token: str) -> str:
        """Hash token for storage and lookup."""
        return hashlib.sha256(token.encode()).hexdigest()

    def _encrypt_token(self, token: str) -> str:
        """Encrypt token for storage."""
        return self._fernet.encrypt(token.encode()).decode()

    def _decrypt_token(self, encrypted: str) -> str:
        """Decrypt token from storage."""
        return self._fernet.decrypt(encrypted.encode()).decode()

    def donate_token(
        self,
        user_id: int,
        refresh_token: str,
        visibility: str = "private"
    ) -> Tuple[bool, str]:
        """
        Donate a refresh token.

        Returns:
            (success, message) tuple
        """
        token_hash = self._hash_token(refresh_token)
        encrypted = self._encrypt_token(refresh_token)
        now = int(time.time() * 1000)

        with self._lock:
            with self._get_conn() as conn:
                # Check for duplicate
                existing = conn.execute(
                    "SELECT id FROM tokens WHERE token_hash = ?", (token_hash,)
                ).fetchone()
                if existing:
                    return False, "Token 已存在"

                conn.execute(
                    """INSERT INTO tokens
                       (user_id, refresh_token_encrypted, token_hash, visibility, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, encrypted, token_hash, visibility, now)
                )
                return True, "Token 捐献成功"

    def get_user_tokens(self, user_id: int) -> List[DonatedToken]:
        """Get all tokens for a user."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM tokens WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [self._row_to_token(r) for r in rows]

    def get_public_tokens(self, status: str = "active") -> List[DonatedToken]:
        """Get all public tokens with given status."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM tokens WHERE visibility = 'public' AND status = ?",
                (status,)
            ).fetchall()
            return [self._row_to_token(r) for r in rows]

    def get_all_active_tokens(self) -> List[DonatedToken]:
        """Get all active tokens (for health check)."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM tokens WHERE status = 'active'"
            ).fetchall()
            return [self._row_to_token(r) for r in rows]

    def get_token_by_id(self, token_id: int) -> Optional[DonatedToken]:
        """Get token by ID."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM tokens WHERE id = ?", (token_id,)).fetchone()
            return self._row_to_token(row) if row else None

    def get_decrypted_token(self, token_id: int) -> Optional[str]:
        """Get decrypted refresh token by ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT refresh_token_encrypted FROM tokens WHERE id = ?", (token_id,)
            ).fetchone()
            if row:
                return self._decrypt_token(row[0])
            return None

    def set_token_visibility(self, token_id: int, visibility: str) -> bool:
        """Set token visibility (public/private)."""
        if visibility not in ("public", "private"):
            return False
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE tokens SET visibility = ? WHERE id = ?",
                    (visibility, token_id)
                )
                return True

    def set_token_status(self, token_id: int, status: str) -> bool:
        """Set token status (active/invalid/expired)."""
        if status not in ("active", "invalid", "expired"):
            return False
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE tokens SET status = ? WHERE id = ?",
                    (status, token_id)
                )
                return True

    def delete_token(self, token_id: int, user_id: Optional[int] = None) -> bool:
        """Delete a token. If user_id provided, verify ownership."""
        with self._lock:
            with self._get_conn() as conn:
                if user_id:
                    conn.execute(
                        "DELETE FROM tokens WHERE id = ? AND user_id = ?",
                        (token_id, user_id)
                    )
                else:
                    conn.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
                return True

    def record_token_usage(self, token_id: int, success: bool) -> None:
        """Record token usage result."""
        now = int(time.time() * 1000)
        with self._lock:
            with self._get_conn() as conn:
                if success:
                    conn.execute(
                        "UPDATE tokens SET success_count = success_count + 1, last_used = ? WHERE id = ?",
                        (now, token_id)
                    )
                else:
                    conn.execute(
                        "UPDATE tokens SET fail_count = fail_count + 1, last_used = ? WHERE id = ?",
                        (now, token_id)
                    )

    def record_health_check(self, token_id: int, is_valid: bool, error_msg: Optional[str] = None) -> None:
        """Record token health check result."""
        now = int(time.time() * 1000)
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO token_health (token_id, check_time, is_valid, error_msg) VALUES (?, ?, ?, ?)",
                    (token_id, now, 1 if is_valid else 0, error_msg)
                )
                conn.execute(
                    "UPDATE tokens SET last_check = ? WHERE id = ?",
                    (now, token_id)
                )
                # Keep only last 10 health checks per token
                conn.execute(
                    """DELETE FROM token_health WHERE id NOT IN
                       (SELECT id FROM token_health WHERE token_id = ? ORDER BY check_time DESC LIMIT 10)
                       AND token_id = ?""",
                    (token_id, token_id)
                )

    def get_token_count(self, user_id: Optional[int] = None) -> Dict[str, int]:
        """Get token counts."""
        with self._get_conn() as conn:
            if user_id:
                total = conn.execute("SELECT COUNT(*) FROM tokens WHERE user_id = ?", (user_id,)).fetchone()[0]
                public = conn.execute(
                    "SELECT COUNT(*) FROM tokens WHERE user_id = ? AND visibility = 'public'", (user_id,)
                ).fetchone()[0]
                active = conn.execute(
                    "SELECT COUNT(*) FROM tokens WHERE user_id = ? AND status = 'active'", (user_id,)
                ).fetchone()[0]
            else:
                total = conn.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
                public = conn.execute("SELECT COUNT(*) FROM tokens WHERE visibility = 'public'").fetchone()[0]
                active = conn.execute("SELECT COUNT(*) FROM tokens WHERE status = 'active'").fetchone()[0]
            return {"total": total, "public": public, "active": active}

    def _row_to_token(self, row: sqlite3.Row) -> DonatedToken:
        """Convert database row to DonatedToken object."""
        return DonatedToken(
            id=row["id"],
            user_id=row["user_id"],
            token_hash=row["token_hash"],
            visibility=row["visibility"],
            status=row["status"],
            success_count=row["success_count"],
            fail_count=row["fail_count"],
            last_used=row["last_used"],
            last_check=row["last_check"],
            created_at=row["created_at"]
        )

    # ==================== API Key Methods ====================

    def generate_api_key(self, user_id: int, name: Optional[str] = None) -> Tuple[str, APIKey]:
        """
        Generate a new API key for user.

        Returns:
            (plain_key, APIKey object) - plain_key is only returned once!
        """
        # Generate sk-xxx format key
        random_part = secrets.token_hex(24)  # 48 chars
        plain_key = f"sk-{random_part}"
        key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
        key_prefix = f"sk-{random_part[:4]}...{random_part[-4:]}"
        now = int(time.time() * 1000)

        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    """INSERT INTO api_keys (user_id, key_hash, key_prefix, name, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, key_hash, key_prefix, name, now)
                )
                key_id = cursor.lastrowid
                api_key = APIKey(
                    id=key_id,
                    user_id=user_id,
                    key_prefix=key_prefix,
                    name=name,
                    is_active=True,
                    request_count=0,
                    last_used=None,
                    created_at=now
                )
                return plain_key, api_key

    def verify_api_key(self, plain_key: str) -> Optional[Tuple[int, APIKey]]:
        """
        Verify an API key.

        Returns:
            (user_id, APIKey) if valid, None otherwise
        """
        if not plain_key.startswith("sk-"):
            return None

        key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1",
                (key_hash,)
            ).fetchone()
            if row:
                api_key = self._row_to_apikey(row)
                return api_key.user_id, api_key
        return None

    def get_user_api_keys(self, user_id: int) -> List[APIKey]:
        """Get all API keys for a user."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [self._row_to_apikey(r) for r in rows]

    def revoke_api_key(self, key_id: int, user_id: Optional[int] = None) -> bool:
        """Revoke an API key. If user_id provided, verify ownership."""
        with self._lock:
            with self._get_conn() as conn:
                if user_id:
                    conn.execute(
                        "UPDATE api_keys SET is_active = 0 WHERE id = ? AND user_id = ?",
                        (key_id, user_id)
                    )
                else:
                    conn.execute("UPDATE api_keys SET is_active = 0 WHERE id = ?", (key_id,))
                return True

    def delete_api_key(self, key_id: int, user_id: Optional[int] = None) -> bool:
        """Delete an API key. If user_id provided, verify ownership."""
        with self._lock:
            with self._get_conn() as conn:
                if user_id:
                    conn.execute(
                        "DELETE FROM api_keys WHERE id = ? AND user_id = ?",
                        (key_id, user_id)
                    )
                else:
                    conn.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
                return True

    def record_api_key_usage(self, key_id: int) -> None:
        """Record API key usage."""
        now = int(time.time() * 1000)
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE api_keys SET request_count = request_count + 1, last_used = ? WHERE id = ?",
                    (now, key_id)
                )

    def get_api_key_count(self, user_id: Optional[int] = None) -> int:
        """Get API key count."""
        with self._get_conn() as conn:
            if user_id:
                return conn.execute(
                    "SELECT COUNT(*) FROM api_keys WHERE user_id = ? AND is_active = 1", (user_id,)
                ).fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1").fetchone()[0]

    def _row_to_apikey(self, row: sqlite3.Row) -> APIKey:
        """Convert database row to APIKey object."""
        return APIKey(
            id=row["id"],
            user_id=row["user_id"],
            key_prefix=row["key_prefix"],
            name=row["name"],
            is_active=bool(row["is_active"]),
            request_count=row["request_count"],
            last_used=row["last_used"],
            created_at=row["created_at"]
        )

    # ==================== Admin Stats ====================

    def get_admin_stats(self) -> Dict:
        """Get statistics for admin dashboard."""
        with self._get_conn() as conn:
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            token_count = conn.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
            public_token_count = conn.execute(
                "SELECT COUNT(*) FROM tokens WHERE visibility = 'public'"
            ).fetchone()[0]
            active_token_count = conn.execute(
                "SELECT COUNT(*) FROM tokens WHERE status = 'active'"
            ).fetchone()[0]
            api_key_count = conn.execute(
                "SELECT COUNT(*) FROM api_keys WHERE is_active = 1"
            ).fetchone()[0]

            return {
                "userCount": user_count,
                "tokenCount": token_count,
                "publicTokenCount": public_token_count,
                "activeTokenCount": active_token_count,
                "apiKeyCount": api_key_count
            }

    # ==================== Admin Management Methods ====================

    def get_all_users(self) -> List[User]:
        """Get all registered users."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            ).fetchall()
            return [self._row_to_user(r) for r in rows]

    def set_user_banned(self, user_id: int, banned: bool) -> bool:
        """Ban or unban a user."""
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE users SET is_banned = ? WHERE id = ?",
                    (1 if banned else 0, user_id)
                )
                return True

    def get_public_tokens_with_users(self, status: str = "active") -> List[Dict]:
        """Get public tokens with user information for user page."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT t.*, u.username
                   FROM tokens t
                   LEFT JOIN users u ON t.user_id = u.id
                   WHERE t.visibility = 'public' AND t.status = ?
                   ORDER BY t.success_count DESC""",
                (status,)
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "username": r["username"] or "Anonymous",
                    "status": r["status"],
                    "success_count": r["success_count"],
                    "fail_count": r["fail_count"],
                    "success_rate": r["success_count"] / max(r["success_count"] + r["fail_count"], 1),
                    "last_used": r["last_used"],
                }
                for r in rows
            ]

    def get_all_tokens_with_users(self) -> List[Dict]:
        """Get all tokens with user information for admin panel."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT t.*, u.username
                   FROM tokens t
                   LEFT JOIN users u ON t.user_id = u.id
                   ORDER BY t.created_at DESC"""
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "username": r["username"],
                    "visibility": r["visibility"],
                    "status": r["status"],
                    "success_count": r["success_count"],
                    "fail_count": r["fail_count"],
                    "success_rate": r["success_count"] / max(r["success_count"] + r["fail_count"], 1),
                    "last_used": r["last_used"],
                    "created_at": r["created_at"]
                }
                for r in rows
            ]

    def admin_delete_token(self, token_id: int) -> bool:
        """Admin: delete any token regardless of ownership."""
        with self._lock:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
                return True


# Global database instance
user_db = UserDatabase()
