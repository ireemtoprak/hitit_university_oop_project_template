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
        SportClub("Mühendislik Spor Kulubü", "Takım ruhu ve disiplin", "Basketbol", 30),
        MusicClub("Ritim Atölyesi", "Müzik yapmak isteyenlere", 12, True),
        ScienceClub("Bilim Topluluğu", "Projeler ve deneyler", 2, True),
    ]

    for c in clubs:
        service.create_club(c)

    service.add_member_to_club("Mühendislik Spor Kulubü", 10)
    service.add_member_to_club("Ritim Atölyesi", 5)
    service.remove_member_from_club("Mühendislik Spor Kulubü", 2)

    e1 = ClubEvent(
        event_id=0,
        club_name="Mühendislik Spor Kulubü",
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

    print("\n--- Mühendislik Spor Kulubü Etkinlikleri ---")
    for ev in service.list_club_events("Mühendislik Spor Kulubü"):
        print(ev)


# Amaç: FileClubRepository ve FileEventRepository çalışıyor mu görmek

# implementations modülünü "factory" gibi kullanıyoruz
import app.modules.module_4.implementations as impl

from app.modules.module_4.repository import FileClubRepository, FileEventRepository


def run_demo_file_repo() -> None:
    club_repo = FileClubRepository("data/module_4/clubs.json")
    event_repo = FileEventRepository("data/module_4/events.json")

    # 1) Kulüp ekleme
    spor = impl.SportClub("Mühendislik Spor", "File repo test", "Futbol", 25)
    muzik = impl.MusicClub("Nota Kulübü", "File repo test", 8, True)

    # Dosyada aynı isim varsa hata verir, o yüzden try/except kullandım.
    try:
        club_repo.add_club(spor)
    except Exception:
        pass

    try:
        club_repo.add_club(muzik)
    except Exception:
        pass

    # 2) Kulüpleri dosyadan geri okumak için
    clubs = club_repo.list_all(factory=impl)
    print("--- File Repo Kulüpler ---")
    for c in clubs:
        print(c.get_info())
        print("-" * 30)

    # 3) Event ekleyelim (dosyaya yazılacak)
    e1 = ClubEvent(
        event_id=0,
        club_name="Mühendislik Spor",
        title="Saha Antrenmanı",
        date=datetime.now() + timedelta(days=1),
        location="Stadyum",
        quota=20,
        event_type="Sport",
    )
    event_repo.add_event(e1)

    # 4) Eventleri dosyadan geri okuyoruz
    events = event_repo.list_by_club("Mühendislik Spor", event_class=impl.ClubEvent)
    print("\n--- Mühendislik Spor Etkinlikleri (File Repo) ---")
    for ev in events:
        print(ev)


if __name__ == "__main__":
    run_demo_file_repo()
