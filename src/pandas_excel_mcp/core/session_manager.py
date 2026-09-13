"""In-memory session tracking.

A "session" groups together the datasets uploaded by one MCP client
connection. V1 storage is in-process memory; swap this for a persistent
store (Redis/DB) in V2 without touching callers.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from ..config.settings import settings
from ..schemas.exceptions import ValidationError
from ..utils.security import new_id


@dataclass
class Session:
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    dataset_ids: set[str] = field(default_factory=set)

    def touch(self) -> None:
        self.last_active = time.time()

    def is_expired(self) -> bool:
        return (time.time() - self.last_active) > settings.session_idle_seconds


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        sid = new_id("session")
        session = Session(session_id=sid)
        self._sessions[sid] = session
        return session

    def get_or_create(self, session_id: str | None) -> Session:
        self._evict_expired()
        if session_id and session_id in self._sessions:
            s = self._sessions[session_id]
            s.touch()
            return s
        return self.create_session()

    def attach_dataset(self, session: Session, dataset_id: str) -> None:
        if len(session.dataset_ids) >= settings.max_datasets_per_session:
            raise ValidationError(
                "Session has reached the maximum number of datasets "
                f"({settings.max_datasets_per_session}).",
            )
        session.dataset_ids.add(dataset_id)
        session.touch()

    def owns_dataset(self, session: Session, dataset_id: str) -> bool:
        return dataset_id in session.dataset_ids

    def _evict_expired(self) -> None:
        expired = [sid for sid, s in self._sessions.items() if s.is_expired()]
        for sid in expired:
            del self._sessions[sid]
