# app/modules/module_4/repository.py

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Iterable


class InMemoryClubRepository:

    def __init__(self) -> None:
        self._clubs_by_name: Dict[str, Any] = {}

    def add_club(self, club: Any) -> None:
        if club is None or getattr(club, "name", None) is None:
            raise ValueError("Kulüp boş olamaz.")

        if club.name in self._clubs_by_name:
            raise ValueError("Bu isimde kulüp zaten var.")

        self._clubs_by_name[club.name] = club

    def list_all(self) -> List[Any]:
        return list(self._clubs_by_name.values())

    def get_by_name(self, club_name: str) -> Optional[Any]:
        return self._clubs_by_name.get(club_name)

    def search(self, keyword: str) -> List[Any]:
        if keyword is None:
            return []
        k = keyword.strip().lower()
        if not k:
            return []
        return [c for c in self.list_all() if k in c.name.lower()]


class InMemoryEventRepository:

    def __init__(self) -> None:
        self._events: List[Any] = []
        self._next_id: int = 1

    def add_event(self, event: Any) -> Any:
        if getattr(event, "event_id", None) in (None, 0):
            event.event_id = self._next_id
            self._next_id += 1
        self._events.append(event)
        return event

    def list_all(self) -> List[Any]:
        return list(self._events)

    def list_by_club(self, club_name: str) -> List[Any]:
        if club_name is None:
            return []
        return [e for e in self._events if e.club_name == club_name]

    @staticmethod
    def is_future_date(date: datetime) -> bool:
        if date is None:
            return False
        return date > datetime.now()

    @classmethod
    def create_with_seed(cls, seed_events: Iterable[Any]) -> "InMemoryEventRepository":
        repo = cls()
        for ev in seed_events:
            repo.add_event(ev)
        return repo
