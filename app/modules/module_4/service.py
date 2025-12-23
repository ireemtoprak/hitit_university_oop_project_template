# app/modules/module_4/service.py

from __future__ import annotations

from datetime import datetime

from app.modules.module_4.base import Club
from app.modules.module_4.implementations import ClubEvent
from app.modules.module_4.repository import ClubRepository, EventRepository


# Kulüp ve etkinlik iş kurallarını yöneten servis sınıfı.
class ClubService:
    # Servisi çalıştırmak için kulüp ve event repo bağlar.
    def __init__(self, club_repo: ClubRepository, event_repo: EventRepository) -> None:
        self.__club_repo: ClubRepository = club_repo
        self.__event_repo: EventRepository = event_repo

    # Yeni kulüp oluşturur ve repo'ya kaydeder.
    def create_club(self, club: Club) -> Club:
        return self.__club_repo.add_club(club)

    # Kulübe isimle üye ekler (başarısızsa False).
    def add_member_to_club(self, club_name: str, count: int) -> bool:
        club = self.__club_repo.get_by_name(club_name)
        if club is None:
            return False
        before = club.member_count
        club.add_member(count)
        if club.member_count != before and hasattr(self.__club_repo, "update_club"):
            self.__club_repo.update_club(club)
        return True

    # Kulüpten isimle üye çıkarır (başarısızsa False).
    def remove_member_from_club(self, club_name: str, count: int) -> bool:
        club = self.__club_repo.get_by_name(club_name)
        if club is None:
            return False
        before = club.member_count
        club.remove_member(count)
        if club.member_count != before and hasattr(self.__club_repo, "update_club"):
            self.__club_repo.update_club(club)
        return True

    # Etkinlik planlar (kulüp var mı, tarih ve kontenjan uygun mu).
    def plan_event(self, event: ClubEvent) -> ClubEvent | None:
        club = self.__club_repo.get_by_id(event.club_id)
        if club is None:
            return None
        if not ClubEvent.is_valid_quota(event.quota):
            return None
        if not self.is_future_date(event.date):
            return None
        if event.club_name.strip() == "":
            event.club_name = club.name
        return self.__event_repo.add_event(event)

    # Belirli bir kulübün tüm etkinliklerini listeler.
    def list_events_of_club(self, club_name: str) -> list[ClubEvent]:
        club = self.__club_repo.get_by_name(club_name)
        if club is None or club.id is None:
            return []
        return self.__event_repo.list_by_club(club.id)

    # Tüm kulüpler arasında isimle arama yapar.
    def search_clubs(self, keyword: str) -> list[Club]:
        if hasattr(self.__club_repo, "search"):
            return self.__club_repo.search(keyword)
        k = (keyword or "").strip().lower()
        return [c for c in self.__club_repo.list_all() if k in c.name.lower()] if k else []

    # Kulüpleri türüne göre filtreler.
    def filter_clubs_by_type(self, club_type: str) -> list[Club]:
        if hasattr(self.__club_repo, "filter_by_type"):
            return self.__club_repo.filter_by_type(club_type)
        t = (club_type or "").strip()
        return [c for c in self.__club_repo.list_all() if c.club_type() == t] if t else []

    # Kulüpleri minimum üye sayısına göre filtreler.
    def filter_clubs_by_min_members(self, min_members: int) -> list[Club]:
        if hasattr(self.__club_repo, "filter_by_min_members"):
            return self.__club_repo.filter_by_min_members(min_members)
        if not isinstance(min_members, int) or min_members < 0:
            return []
        return [c for c in self.__club_repo.list_all() if c.member_count >= min_members]

    # Etkinlikleri tarih aralığına göre filtreler.
    def filter_events_by_date_range(self, start: datetime, end: datetime) -> list[ClubEvent]:
        return self.__event_repo.list_by_date_range(start, end)

    # Etkinlikleri türe göre filtreler.
    def filter_events_by_type(self, event_type: str) -> list[ClubEvent]:
        return self.__event_repo.list_by_type(event_type)

    # Etkinliği id ile iptal eder.
    def cancel_event(self, event_id: int) -> bool:
        return self.__event_repo.remove_by_id(event_id)

    # Tarihin gelecekte olup olmadığını kontrol eder.
    @staticmethod
    def is_future_date(date: datetime) -> bool:
        return isinstance(date, datetime) and date > datetime.now()

    # Repo seçimiyle servis üreten yardımcı kurucu metottur.
    @classmethod
    def from_repos(cls, club_repo: ClubRepository, event_repo: EventRepository) -> "ClubService":
        return cls(club_repo=club_repo, event_repo=event_repo)
