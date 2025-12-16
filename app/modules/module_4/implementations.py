from dataclasses import dataclass
from app.modules.module_4.base import Club


class SportClub(Club):

    def __init__(self, name: str, description: str, sport_name: str, max_members: int):
        super().__init__(name, description)

        self.sport_name = sport_name
        self.max_members = max_members

    def add_member(self, count: int) -> None:
        # Üye eklerken kapasiteyi aşmaması için
        if count > 0 and self.member_count + count <= self.max_members:
            self.member_count += count

    def remove_member(self, count: int) -> None:
        # Üye çıkarırken sayı negatif olmasın diye
        if count > 0 and self.member_count - count >= 0:
            self.member_count -= count

    def club_type(self) -> str:
        
        return "SportClub"


class MusicClub(Club):

    def __init__(self, name: str, description: str, instrument_count: int, has_studio: bool):
        super().__init__(name, description)

        self.instrument_count = instrument_count
        self.has_studio = has_studio

    def add_member(self, count: int) -> None:
        # Müzik kulübünde kapasite sınırı yok
        if count > 0:
            self.member_count += count

    def remove_member(self, count: int) -> None:
        # Üye çıkarma işlemi
        if count > 0 and self.member_count - count >= 0:
            self.member_count -= count

    def club_type(self) -> str:
        
        return "MusicClub"


class ScienceClub(Club):

    def __init__(self, name: str, description: str, lab_count: int, project_based: bool):
        super().__init__(name, description)

        self.lab_count = lab_count
        self.project_based = project_based

    def add_member(self, count: int) -> None:
        # Bilim kulübünde üye ekleme
        if count > 0:
            self.member_count += count

    def remove_member(self, count: int) -> None:
        # Üye sayısı sıfırın altına düşmesin diye
        if count > 0 and self.member_count - count >= 0:
            self.member_count -= count

    def club_type(self) -> str:

        return "ScienceClub"
    
    from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClubEvent:
    # Etkinlik bilgileri
    event_id: int
    club_name: str
    title: str
    date: datetime
    location: str
    quota: int
    event_type: str = "General"


class ClubService:

    def __init__(self, club_repo, event_repo):
        self.club_repo = club_repo
        self.event_repo = event_repo

    def create_club(self, club) -> None:
        # Yeni kulüp kaydetme
        self.club_repo.add_club(club)

    def add_member_to_club(self, club_name: str, count: int) -> bool:
        # Kulübe üye ekleme
        club = self.club_repo.get_by_name(club_name)
        if club is None:
            return False
        club.add_member(count)
        return True

    def remove_member_from_club(self, club_name: str, count: int) -> bool:
        # Kulüpten üye çıkarma
        club = self.club_repo.get_by_name(club_name)
        if club is None:
            return False
        club.remove_member(count)
        return True

    def plan_event(self, event: ClubEvent) -> bool:
        # Etkinlik planlama
        club = self.club_repo.get_by_name(event.club_name)
        if club is None:
            return False

        if not self.is_valid_quota(event.quota):
            return False

        self.event_repo.add_event(event)
        return True

    def list_club_events(self, club_name: str):
        # Bir kulübün tüm etkinliklerini listeler
        return self.event_repo.list_by_club(club_name)

    def search_clubs(self, keyword: str):
        # Kulüp arama (isimden)
        return self.club_repo.search(keyword)

    @staticmethod
    def is_valid_quota(quota: int) -> bool:
        # Kontenjan 0'dan büyük olmalı
        return quota > 0

