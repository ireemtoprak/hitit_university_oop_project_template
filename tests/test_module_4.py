# tests/test_module_4.py
# Module 4 (Clubs) testleri

from datetime import datetime, timedelta

from app.modules.module_4.repository import InMemoryClubRepository, InMemoryEventRepository
from app.modules.module_4.implementations import (
    SportClub,
    MusicClub,
    ScienceClub,
    ClubEvent,
    ClubService,
)


def test_get_info_type_yazar():
    # get_info çıktısında temel alanların ve doğru club_type bilgisinin yazdığını doğrular
    c = SportClub("Test Spor", "açıklama", "Futbol", 10)
    info = c.get_info()

    assert "name:" in info
    assert "member_count:" in info
    assert "description:" in info
    assert "created_at:" in info
    assert "type:" in info
    assert "SportClub" in info


def test_sportclub_kapasite_asamaz():
    # SportClub'ın max_members kapasitesini aşan üye eklemeyi engellediğini test eder
    c = SportClub("Kapasite", "deneme", "Basketbol", 5)

    c.add_member(6)  # kapasiteyi aşarsa eklememeli
    assert c.member_count == 0

    c.add_member(3)
    assert c.member_count == 3

    c.add_member(3)  # 3 + 3 = 6 > 5
    assert c.member_count == 3


def test_remove_member_sifirin_altina_inmez():
    # Üye çıkarma işleminin member_count değerini 0'ın altına düşürmediğini kontrol eder
    c = MusicClub("Müzik", "deneme", 5, False)

    c.add_member(2)
    c.remove_member(5)  # fazla çıkarma -> düşmemeli
    assert c.member_count == 2

    c.remove_member(2)
    assert c.member_count == 0


def test_club_repo_add_get_search():
    # InMemoryClubRepository'nin ekleme, isimle bulma ve arama fonksiyonlarının doğru çalıştığını test eder
    repo = InMemoryClubRepository()

    c1 = ScienceClub("Bilim", "projeler", 2, True)
    c2 = MusicClub("Ritim", "müzik", 10, True)

    repo.add_club(c1)
    repo.add_club(c2)

    assert repo.get_by_name("Bilim") is not None
    assert repo.get_by_name("Ritim") is not None

    # aramada küçük/büyük harf fark etmemeli
    out = repo.search("bi")
    assert len(out) == 1
    assert out[0].name == "Bilim"


def test_service_add_remove_member_true_false():
    # ClubService'in kulüp yokken False, kulüp varken True dönerek üye ekleme/çıkarma yaptığını doğrular
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    # kulüp yoksa False dönmeli
    assert service.add_member_to_club("Yok", 1) is False
    assert service.remove_member_from_club("Yok", 1) is False

    club = SportClub("Kulüp", "deneme", "Voleybol", 10)
    service.create_club(club)

    # kulüp varsa True dönmeli
    assert service.add_member_to_club("Kulüp", 3) is True
    assert club.member_count == 3

    assert service.remove_member_from_club("Kulüp", 2) is True
    assert club.member_count == 1


def test_service_plan_event_kulup_yoksa_false():
    # Kulüp bulunamazsa plan_event çağrısının False döndürdüğünü test eder
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    e = ClubEvent(
        event_id=0,
        club_name="Kulüp Yok",
        title="Etkinlik",
        date=datetime.now() + timedelta(days=1),
        location="Salon",
        quota=10,
        event_type="General",
    )

    assert service.plan_event(e) is False


def test_service_plan_event_quota_gecersizse_false():
    # Kontenjan geçersizse (0 veya negatif) plan_event çağrısının False döndürdüğünü test eder
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    club = MusicClub("Müzik Kulübü", "deneme", 10, True)
    service.create_club(club)

    e = ClubEvent(
        event_id=0,
        club_name="Müzik Kulübü",
        title="Konser",
        date=datetime.now() + timedelta(days=2),
        location="Konferans",
        quota=0,  # geçersiz
        event_type="Music",
    )

    assert service.plan_event(e) is False


def test_service_plan_event_olunca_listede_gozukur_ve_id_alir():
    # Etkinlik planlanınca listede göründüğünü ve repo tarafından event_id verildiğini doğrular
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    club = SportClub("Spor Kulübü", "deneme", "Basketbol", 50)
    service.create_club(club)

    e1 = ClubEvent(
        event_id=0,
        club_name="Spor Kulübü",
        title="Antrenman",
        date=datetime.now() + timedelta(days=3),
        location="Spor Salonu",
        quota=20,
        event_type="Sport",
    )

    ok = service.plan_event(e1)
    assert ok is True

    events = service.list_club_events("Spor Kulübü")
    assert len(events) == 1
    assert events[0].title == "Antrenman"

    # event_id repo tarafından verilmeli (0 kalmamalı)
    assert events[0].event_id != 0


def test_service_search_clubs():
    # ClubService.search_clubs aramasının küçük/büyük harf fark etmeden doğru kulübü bulduğunu test eder
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    service.create_club(ScienceClub("Bilim", "x", 1, True))
    service.create_club(MusicClub("Müzik", "y", 1, False))

    out = service.search_clubs("mü")
    # "Müzik" yakalamalı
    assert len(out) == 1
    assert out[0].name == "Müzik"


def test_static_is_valid_quota():
    # ClubService.is_valid_quota statik metodunun pozitif/değerleri doğru değerlendirdiğini test eder
    assert ClubService.is_valid_quota(1) is True
    assert ClubService.is_valid_quota(0) is False
    assert ClubService.is_valid_quota(-5) is False
