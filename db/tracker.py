"""
제품 트래킹 및 피부 일지 DB 모듈 (SQLite)

사용 중인 제품과 피부 상태 일지를 저장하고 불러옵니다.
chat_history.db 와 같은 DB 파일을 공유합니다.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import date

logger = logging.getLogger("beauilt-agent.tracker")

_DB_PATH = Path(__file__).parent.parent / "data" / "chat_history.db"

CATEGORIES = ["클렌저", "토너", "세럼", "모이스처라이저", "선크림", "기타"]
END_REASONS = ["트러블발생", "효과없음", "사용완료", "기타"]


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_tracker_db() -> None:
    """트래킹 테이블이 없으면 생성"""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                brand       TEXT,
                category    TEXT    NOT NULL,
                ingredients TEXT,
                started_at  TEXT    NOT NULL,
                ended_at    TEXT,
                end_reason  TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skin_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date   TEXT    NOT NULL UNIQUE,
                moisture   INTEGER NOT NULL,
                oiliness   INTEGER NOT NULL,
                trouble    INTEGER NOT NULL,
                memo       TEXT,
                created_at TEXT    NOT NULL
            )
        """)


# ── 제품 ──────────────────────────────────────────────────────────────────────

def add_product(name: str, brand: str, category: str,
                started_at: str, ingredients: str = "") -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO products (name, brand, category, ingredients, started_at) VALUES (?, ?, ?, ?, ?)",
            (name, brand.strip(), category, ingredients.strip(), started_at),
        )


def stop_product(product_id: int, ended_at: str, end_reason: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE products SET ended_at = ?, end_reason = ? WHERE id = ?",
            (ended_at, end_reason, product_id),
        )


def list_active_products() -> List[Dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE ended_at IS NULL ORDER BY started_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def list_all_products() -> List[Dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY started_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


# ── 피부 일지 ─────────────────────────────────────────────────────────────────

def save_skin_log(log_date: str, moisture: int, oiliness: int,
                  trouble: int, memo: str = "") -> None:
    from datetime import datetime
    with _connect() as conn:
        conn.execute("""
            INSERT INTO skin_logs (log_date, moisture, oiliness, trouble, memo, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(log_date) DO UPDATE SET
                moisture = excluded.moisture,
                oiliness = excluded.oiliness,
                trouble  = excluded.trouble,
                memo     = excluded.memo,
                created_at = excluded.created_at
        """, (log_date, moisture, oiliness, trouble, memo.strip(), datetime.now().isoformat()))


def list_recent_skin_logs(limit: int = 10) -> List[Dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM skin_logs ORDER BY log_date DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_skin_log(log_date: str) -> Optional[Dict]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM skin_logs WHERE log_date = ?", (log_date,)
        ).fetchone()
    return dict(row) if row else None
