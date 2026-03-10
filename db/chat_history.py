"""
대화 히스토리 영속성 모듈 (SQLite)

세션별 대화 내용을 저장하고 불러옵니다.
DB 파일은 프로젝트 루트의 data/chat_history.db 에 저장됩니다.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger("beauilt-agent.db")

_DB_PATH = Path(__file__).parent.parent / "data" / "chat_history.db"


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """테이블이 없으면 생성"""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT    NOT NULL,
                role      TEXT    NOT NULL,
                content   TEXT    NOT NULL,
                created_at TEXT   NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id, id)"
        )


def save_message(session_id: str, role: str, content: str) -> None:
    """메시지 한 건 저장"""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat()),
            )
    except Exception as e:
        logger.error("메시지 저장 실패: %s", e, exc_info=True)


def load_session(session_id: str) -> List[Dict[str, str]]:
    """세션의 전체 메시지 로드"""
    try:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception as e:
        logger.error("세션 로드 실패: %s", e, exc_info=True)
        return []


def list_recent_sessions(limit: int = 10) -> List[Dict[str, str]]:
    """
    최근 세션 목록 반환 (사이드바 표시용)
    각 세션의 첫 번째 사용자 메시지와 시작 시각을 반환합니다.
    """
    try:
        with _connect() as conn:
            rows = conn.execute("""
                SELECT
                    session_id,
                    MIN(created_at) AS started_at,
                    MIN(CASE WHEN role = 'user' THEN content END) AS preview
                FROM messages
                GROUP BY session_id
                ORDER BY started_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
        return [
            {
                "session_id": r["session_id"],
                "started_at": r["started_at"][:16].replace("T", " "),
                "preview": (r["preview"] or "")[:30] + "...",
            }
            for r in rows
        ]
    except Exception as e:
        logger.error("세션 목록 로드 실패: %s", e, exc_info=True)
        return []


def delete_session(session_id: str) -> None:
    """세션 삭제"""
    try:
        with _connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    except Exception as e:
        logger.error("세션 삭제 실패: %s", e, exc_info=True)
