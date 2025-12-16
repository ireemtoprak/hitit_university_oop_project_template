# app/modules/module_4/demo.py

from datetime import datetime, timedelta

from app.modules.module_4.base import Club
from app.modules.module_4.repository import InMemoryClubRepository, InMemoryEventRepository
from app.modules.module_4.implementations import (
    ClubEvent,
    ClubService,
    SportClub,
    MusicClub,
    ScienceClub,
)


def run_demo() -> None:
    club_repo = InMemoryClubRepository()
    event_repo = InMemoryEventRepository()
    service = ClubService(club_repo, event_repo)

    clubs: list[Club] = [
        SportClub("Mühendislik Spor Klubü", "Takım ruhu ve disiplin", "Basketbol", 30),
        MusicClub("Ritim Atölyesi", "Müzik yapmak isteyenlere", 12, True),
        ScienceClub("Bilim Topluluğu", "Projeler ve deneyler", 2, True),
    ]

    for c in clubs:
        service.create_club(c)

    service.add_member_to_club("Mühendislik Spor Klubü", 10)
    service.add_member_to_club("Ritim Atölyesi", 5)
    service.remove_member_from_club("Mühendislik Spor Klubü", 2)

    e1 = ClubEvent(
        event_id=0,
        club_name="Mühendislik Spor Klubü",
        title="Antrenman",
        date=datetime.now() + timedelta(days=2),
        location="Spor Salonu",
        quota=20,
        event_type="Sport",
    )

    e2 = ClubEvent(
        event_id=0,
        club_name="Ritim Atölyesi",
        title="Küçük Konser",
        date=datetime.now() + timedelta(days=5),
        location="Konferans Salonu",
        quota=50,
        event_type="Music",
    )

    print("Etkinlik planlama sonuçları:",
          service.plan_event(e1),
          service.plan_event(e2))

    print("\n--- Kulüpler ---")
    for c in club_repo.list_all():
        print(c.get_info())
        print("-" * 30)

    print("\n--- Mühendislik Spor Klubü Etkinlikleri ---")
    for ev in service.list_club_events("Mühendislik Spor Klubü"):
        print(ev)


if __name__ == "__main__":
    run_demo()
