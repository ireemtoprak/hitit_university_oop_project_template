# tests/test_module_4.py

from datetime import datetime, timedelta

from app.modules.module_4.implementations import SportClub, MusicClub, ScienceClub, ClubEvent
from app.modules.module_4.repository import InMemoryClubRepository, InMemoryEventRepository
from app.modules.module_4.service import ClubService


# Farklı türde kulüpler oluşturulabiliyor mu kontrol eder.
def test_create_different_club_types():
    c1 = SportClub("Spor", "Açıklama", "Basketbol", 10)
    c2 = MusicClub("Müzik", "Açıklama", 5, True)
    c3 = ScienceClub("Bilim", "Açıklama", 2, False)

    assert c1.club_type() == "SportClub"
    assert c2.club_type() == "MusicClub"
    assert c3.club_type() == "ScienceClub"


# SportClub kapasiteyi aşınca üye eklememeli.
def test_sportclub_capacity_limit():
    c = SportClub("Spor", "Açıklama", "Futbol", 5)
    c.add_member(6)
    assert c.member_count == 0

    c.add_member(3)
    assert c.member_count == 3

    c.add_member(3)
    assert c.member_count == 3


# Üye çıkarma işlemi 0 altına düşürmemeli.
def test_remove_member_not_below_zero():
    c = MusicClub("Müzik", "Açıklama", 2, False)
    c.add_member(2)
    c.remove_member(5)
    assert c.member_count == 2

    c.remove_member(1)
    assert c.member_count == 1


# Etkinlik oluşturma ve kulüple ilişkilendirme çalışıyor mu kontrol eder.
def test_plan_event_and_link_to_club():
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    club = service.create_club(SportClub("Spor", "Açıklama", "Basketbol", 10))

    ev = ClubEvent(
        event_id=0,
        club_id=club.id,
        club_name=club.name,
        title="Antrenman",
        date=datetime.now() + timedelta(days=1),
        location="Salon",
        quota=10,
        event_type="Sport",
    )

    planned = service.plan_event(ev)
    assert planned is not None
    assert planned.event_id != 0

    events = service.list_events_of_club("Spor")
    assert len(events) == 1
    assert events[0].title == "Antrenman"


# Repo arama/filtreleme işlemleri çalışıyor mu kontrol eder.
def test_search_and_filter():
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    service.create_club(SportClub("Spor Kulübü", "Açıklama", "Basketbol", 20))
    service.create_club(MusicClub("Müzik Kulübü", "Açıklama", 3, True))

    found = service.search_clubs("spor")
    assert len(found) == 1
    assert found[0].name == "Spor Kulübü"

    filtered = service.filter_clubs_by_type("MusicClub")
    assert len(filtered) == 1
    assert filtered[0].club_type() == "MusicClub"


# get_info formatında beklenen alanlar var mı kontrol eder.
def test_get_info_format():
    c = SportClub("Spor", "Açıklama", "Futbol", 10)
    info = c.get_info()

    assert "name:" in info
    assert "member_count:" in info
    assert "description:" in info
    assert "created_at:" in info
    assert "type:" in info
    assert "SportClub" in info
