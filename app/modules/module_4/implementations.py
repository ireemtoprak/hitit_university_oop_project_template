from dataclasses import dataclass
from app.modules.module_4.base import Club


class SportClub(Club):
    # Spor kulübüne özel bilgileri (spor adı ve maksimum üye sayısı) ekleyen sınıf
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
        # Bu nesnenin hangi kulüp türü olduğunu (SportClub) belirtir
        return "SportClub"


class MusicClub(Club):
    # Müzik kulübüne ait enstrüman sayısı ve stüdyo bilgisini tutan sınıf
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
    # Bilim kulübüne ait laboratuvar sayısı ve proje bazlı çalışma bilgisini tutan sınıf
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
        # Bu nesnenin ScienceClub türünde olduğunu belirtir
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
        # Kulüp ve etkinlik işlemlerini yönetmek için repository'leri servise bağlar
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


from datetime import datetime
from typing import Any, Optional, List


class ClubServiceV2:

    def __init__(self, club_repo: Any, event_repo: Any, factory: Any = None):
        # Repo’ları bağlar; file repo kullanımı için factory parametresini saklar
        self.club_repo = club_repo
        self.event_repo = event_repo
        self.factory = factory  # File repo için implementations modülü gibi düşün


    def _club_get_by_name(self, club_name: str):
        # Kulübü ada göre döndürür (InMemory/File repo çağrı farkını yönetir)
        try:
            # InMemory: get_by_name(name)
            return self.club_repo.get_by_name(club_name)
        except TypeError:
            # File: get_by_name(name, factory)
            return self.club_repo.get_by_name(club_name, factory=self.factory)

    def _club_list_all(self):
        # Tüm kulüpleri listeler (InMemory/File repo çağrı farkını yönetir)
        if hasattr(self.club_repo, "list_all"):
            try:
                # InMemory: list_all()
                return self.club_repo.list_all()
            except TypeError:
                # File: list_all(factory=...)
                return self.club_repo.list_all(factory=self.factory)
        return []

    def _club_search(self, keyword: str):
        # Kulüpleri anahtar kelimeye göre arar (InMemory/File repo çağrı farkını yönetir)
        try:
            # InMemory: search(keyword)
            return self.club_repo.search(keyword)
        except TypeError:
            # File: search(keyword, factory)
            return self.club_repo.search(keyword, factory=self.factory)

    def _club_update_if_possible(self, club: Any) -> None:
        # File repo varsa değişen kulüp bilgisini update_club ile dosyaya yazar
        if hasattr(self.club_repo, "update_club"):
            try:
                self.club_repo.update_club(club)
            except Exception:
                pass


    def create_club(self, club: Any) -> None:
        # Yeni kulübü repo’ya kaydeder
        self.club_repo.add_club(club)

    def add_member_to_club(self, club_name: str, count: int) -> bool:
        # Kulüp varsa üye ekler ve gerekiyorsa kalıcı günceller
        club = self._club_get_by_name(club_name)
        if club is None:
            return False
        club.add_member(count)
        self._club_update_if_possible(club)
        return True

    def remove_member_from_club(self, club_name: str, count: int) -> bool:
        # Kulüp varsa üye çıkarır ve gerekiyorsa kalıcı günceller
        club = self._club_get_by_name(club_name)
        if club is None:
            return False
        club.remove_member(count)
        self._club_update_if_possible(club)
        return True

    def plan_event(self, event: "ClubEvent") -> bool:
        # Kulüp varsa ve kontenjan geçerliyse etkinliği repo’ya ekler
        club = self._club_get_by_name(event.club_name)
        if club is None:
            return False

        # eski mantık aynı: kontenjan > 0
        if not ClubService.is_valid_quota(event.quota):
            return False

        self.event_repo.add_event(event)
        return True

    def list_club_events(self, club_name: str):
        # Kulübe ait etkinlikleri listeler (InMemory/File repo uyumlu)
        try:
            # InMemory: list_by_club(name)
            return self.event_repo.list_by_club(club_name)
        except TypeError:
            # File: list_by_club(name, event_class)
            return self.event_repo.list_by_club(club_name, event_class=self.factory.ClubEvent)


    def search_clubs(self, keyword: str):
        # Kulüp aramasını repo üzerinden döndürür
        return self._club_search(keyword)

    def filter_clubs_by_type(self, club_type: str):
        # Kulüpleri türüne göre filtreler (repo destekliyorsa repo, değilse elde)
        if hasattr(self.club_repo, "filter_by_type"):
            try:
                return self.club_repo.filter_by_type(club_type)
            except TypeError:
                return self.club_repo.filter_by_type(club_type, factory=self.factory)

        t = (club_type or "").strip()
        if not t:
            return []
        return [c for c in self._club_list_all() if getattr(c, "club_type", lambda: "")() == t]

    def filter_clubs_by_min_members(self, min_members: int):
        # Kulüpleri minimum üye sayısına göre filtreler (repo destekliyorsa repo, değilse elde)
        if hasattr(self.club_repo, "filter_by_min_members"):
            try:
                return self.club_repo.filter_by_min_members(min_members)
            except TypeError:
                return self.club_repo.filter_by_min_members(min_members, factory=self.factory)

        if not isinstance(min_members, int) or min_members < 0:
            return []
        return [c for c in self._club_list_all() if getattr(c, "member_count", 0) >= min_members]

    def get_club_by_id(self, club_id: int):
       # Kulübü ID’ye göre getirir (repo destekliyorsa kullanır)
        if hasattr(self.club_repo, "get_by_id"):
            try:
                return self.club_repo.get_by_id(club_id)
            except TypeError:
                return self.club_repo.get_by_id(club_id, factory=self.factory)
        return None


    def list_events_by_date_range(self, start: datetime, end: datetime):
        # Etkinlikleri tarih aralığına göre listeler (repo destekliyorsa repo, değilse elde)
        if hasattr(self.event_repo, "list_by_date_range"):
            try:
                return self.event_repo.list_by_date_range(start, end)
            except TypeError:
                return self.event_repo.list_by_date_range(start, end, event_class=self.factory.ClubEvent)

        # Repo metodu yoksa tüm etkinlikler üzerinden elde filtreler
        events = self.list_all_events()
        return [e for e in events if isinstance(getattr(e, "date", None), datetime) and start <= e.date <= end]

    def list_events_by_type(self, event_type: str):
        # Etkinlikleri türüne göre listeler (repo destekliyorsa repo, değilse elde)
        if hasattr(self.event_repo, "list_by_type"):
            try:
                return self.event_repo.list_by_type(event_type)
            except TypeError:
                return self.event_repo.list_by_type(event_type, event_class=self.factory.ClubEvent)

        t = (event_type or "").strip().lower()
        events = self.list_all_events()
        return [e for e in events if str(getattr(e, "event_type", "")).strip().lower() == t]

    def cancel_event(self, event_id: int) -> bool:
        # Etkinliği ID’ye göre siler/iptal eder (remove_by_id varsa)
        if hasattr(self.event_repo, "remove_by_id"):
            return bool(self.event_repo.remove_by_id(event_id))
        return False

    def list_all_events(self):
        # Tüm etkinlikleri döndürür (InMemory/File repo uyumlu)
        if hasattr(self.event_repo, "list_all"):
            try:
                return self.event_repo.list_all()
            except TypeError:
                return self.event_repo.list_all(event_class=self.factory.ClubEvent)
        return []

