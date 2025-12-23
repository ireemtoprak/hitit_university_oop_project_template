# app/modules/module_4/demo.py

from __future__ import annotations

from datetime import datetime, timedelta

from app.modules.module_4.base import Club
from app.modules.module_4.implementations import SportClub, MusicClub, ScienceClub, ClubEvent
from app.modules.module_4.repository import InMemoryClubRepository, InMemoryEventRepository
from app.modules.module_4.service import ClubService


# Ekranı ayırmak için çizgi basar.
def _sep() -> None:
    print("\n" + "=" * 60 + "\n", flush=True)


# Kullanıcının mesajı görmesi için bekletir.
def _pause() -> None:
    input("\nMenüye dönmek için Enter...")


# Boş olmayan metin alır.
def _ask_text(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Boş bırakılamaz.", flush=True)


# (e/h) ile boolean alır.
def _ask_yes_no(prompt: str) -> bool:
    while True:
        s = input(prompt).strip().lower()
        if s in {"e", "evet"}:
            return True
        if s in {"h", "hayır", "hayir"}:
            return False
        print("e/h gir.", flush=True)


# En az min_value olacak şekilde int alır.
def _ask_int(prompt: str, min_value: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
            if min_value is not None and val < min_value:
                print(f"En az {min_value} olmalı.", flush=True)
                continue
            return val
        except ValueError:
            print("Sayı gir.", flush=True)


# Virgülle ayrılmış isim soyisim listesi alır.
def _ask_names(prompt: str) -> list[str]:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("En az 1 isim gir.", flush=True)
            continue
        parts = [p.strip() for p in raw.split(",")]
        names = [p for p in parts if len(p.split()) >= 2]  # en az 2 kelime (isim soyisim)
        if not names:
            print("'İsim Soyisim' girilmeli!", flush=True)
            continue
        return names
    
    
# Kulüp bilgilerini Türkçe etiketlerle ekrana yazdırır.
def print_club_info_tr(club: Club) -> None:
    created_date = club.created_at.strftime("%d.%m.%Y")

    print(f"Ad: {club.name}", flush=True)
    print(f"Üye sayısı: {club.member_count}", flush=True)
    print(f"Açıklama: {club.description}", flush=True)
    print(f"Oluşturulma tarihi: {created_date}", flush=True)
    print(f"Tür: {club.club_type()}", flush=True)


# Kullanıcı tür girişini sınıf adına çevirir.
TYPE_MAP = {
    "spor kulübü": "SportClub",
    "spor": "SportClub",
    "müzik kulübü": "MusicClub",
    "müzik": "MusicClub",
    "bilim kulübü": "ScienceClub",
    "bilim": "ScienceClub",
}

   
# Menü seçeneklerini ekrana basar.
def _print_menu() -> None:
    print("Kulüp / Etkinlik Yönetimi (Etkileşimli Demo)", flush=True)
    print("1) Kulüp oluştur", flush=True)
    print("2) Kulüpleri listele", flush=True)
    print("3) Kulüp bilgisi göster", flush=True)
    print("4) Kulübe üye ekle (isim-soyisim)", flush=True)
    print("5) Kulüpten üye çıkar (isim-soyisim)", flush=True)
    print("6) Etkinlik planla", flush=True)
    print("7) Kulübün etkinliklerini listele", flush=True)
    print("8) Etkinlikleri türüne göre filtrele", flush=True)
    print("9) Etkinlikleri tarih aralığına göre filtrele", flush=True)
    print("10) Kulüp ara", flush=True)
    print("11) Kulüp filtrele (tür)", flush=True)
    print("12) Kulüp filtrele (min üye)", flush=True)
    print("13) Etkinlik iptal et (ID ile)", flush=True)
    print("0) Çıkış", flush=True)


# Kullanıcının seçimine göre kulüp nesnesi üretir.
def _create_club_interactive() -> Club:
    _sep()
    print("Kulüp Türü Seç", flush=True)
    print("1) Spor Kulübü", flush=True)
    print("2) Müzik Kulübü", flush=True)
    print("3) Bilim Kulübü", flush=True)
    t = _ask_int("Seçim: ", 1)

    name = _ask_text("Kulüp adı: ")
    desc = _ask_text("Açıklama: ")

    if t == 1:
        sport_name = _ask_text("Spor branşı: ")
        max_members = _ask_int("Kapasite: ", 1)
        return SportClub(name, desc, sport_name, max_members)

    if t == 2:
        instrument_count = _ask_int("Enstrüman sayısı: ", 0)
        has_studio = _ask_yes_no("Stüdyo var mı? (e/h): ")
        return MusicClub(name, desc, instrument_count, has_studio)

    lab_count = _ask_int("Lab sayısı: ", 0)
    project_based = _ask_yes_no("Proje odaklı mı? (e/h): ")
    return ScienceClub(name, desc, lab_count, project_based)


# Kullanıcıdan bilgi alıp etkinlik nesnesi üretir.
def _create_event_interactive(club_id: int, club_name: str) -> ClubEvent:
    _sep()
    print("Etkinlik Planla", flush=True)
    title = _ask_text("Başlık: ")
    location = _ask_text("Mekan: ")
    quota = _ask_int("Kontenjan: ", 1)
    days = _ask_int("Kaç gün sonra? (0=bugün): ", 0)
    event_type = _ask_text("Etkinlik türü (Spor/Müzik/Bilim/Genel): ")

    return ClubEvent(
        event_id=0,
        club_id=club_id,
        club_name=club_name,
        title=title,
        date=datetime.now() + timedelta(days=days),
        location=location,
        quota=quota,
        event_type=event_type,
    )


# Kulüpleri satır satır özet olarak basar.
def _print_club_list(clubs: list[Club], member_names: dict[str, list[str]]) -> None:
    if not clubs:
        print("Kayıtlı kulüp yok.", flush=True)
        return
    for c in clubs:
        names = member_names.get(c.name, [])
        print(f"- ID={c.id} | Kulüp adı={c.name} | Tür={c.club_type()} | Üye sayısı={c.member_count} | Kayıtlı üye={len(names)}", flush=True)


# Etkinlikleri satır satır özet olarak basar.
def _print_event_list(events: list[ClubEvent]) -> None:
    if not events:
        print("Etkinlik yok.", flush=True)
        return
    for e in events:
        print(f"- ID={e.event_id} | {e.title} | {e.date.strftime('%d.%m.%Y')} | {e.location} | Tür={e.event_type} | Kontenjan={e.quota}", flush=True)


# Tarih filtresi için başlangıç ve bitiş tarihini gün cinsinden alır.
def _ask_date_range_days() -> tuple[datetime, datetime]:
    _sep()
    print("Tarih Aralığı (gün cinsinden)", flush=True)
    start_days = _ask_int("Başlangıç: kaç gün sonra? (0=bugün): ", 0)
    end_days = _ask_int("Bitiş: kaç gün sonra?: ", 0)
    if end_days < start_days:
        start_days, end_days = end_days, start_days
    start = datetime.now() + timedelta(days=start_days)
    end = datetime.now() + timedelta(days=end_days)
    return start, end


# Etkileşimli terminal uygulamasını başlatır.
def main() -> None:
    club_repo = InMemoryClubRepository.empty()
    event_repo = InMemoryEventRepository.empty()
    service = ClubService.from_repos(club_repo, event_repo)

    # Demo içinde üye isimlerini tutmak için yardımcı sözlük.
    member_names: dict[str, list[str]] = {}

    _sep()
    print("Demo hazır!", flush=True)

    while True:
        _sep()
        _print_menu()
        secim = input("\nSeçim: ").strip()

        if secim == "":
            print("Seçim yapmadın. 0-13 arası bir sayı gir.", flush=True)
            _pause()
            continue

        if secim == "0":
            _sep()
            print("Çıkış yapıldı.", flush=True)
            break

        if secim == "1":
            try:
                club = _create_club_interactive()
                saved = service.create_club(club)
                member_names.setdefault(saved.name, [])
                _sep()
                print(f"✅ Kulüp oluşturuldu: {saved.name} (ID={saved.id})", flush=True)
            except Exception as e:
                _sep()
                print(f"❌ Hata: {e}", flush=True)
            _pause()
            continue

        if secim == "2":
            _sep()
            _print_club_list(club_repo.list_all(), member_names)
            _pause()
            continue

        if secim == "3":
            name = _ask_text("Kulüp adı: ")
            club = club_repo.get_by_name(name)
            _sep()
            if club is None:
                print("❌ Kulüp bulunamadı.", flush=True)
            else:
                print("✅ Kulüp bilgisi:", flush=True)
                print_club_info_tr(club)
                if member_names.get(club.name):
                    print("\nÜyeler:", flush=True)
                    for n in member_names[club.name]:
                        print(f"- {n}", flush=True)
            _pause()
            continue

        if secim == "4":
            name = _ask_text("Kulüp adı: ")
            club = club_repo.get_by_name(name)
            if club is None:
                _sep()
                print("❌ Kulüp bulunamadı.", flush=True)
                _pause()
                continue

            names = _ask_names("Eklenecek üyeler (virgülle): ")
            ok = service.add_member_to_club(club.name, len(names))

            _sep()
            if not ok:
                print("❌ Üye eklenemedi.", flush=True)
            else:
                member_names.setdefault(club.name, [])
                member_names[club.name].extend([n for n in names if n not in member_names[club.name]])
                updated = club_repo.get_by_name(club.name)
                print(f"✅ {len(names)} üye eklendi. Güncel üye sayısı: {updated.member_count if updated else '?'}", flush=True)
            _pause()
            continue

        if secim == "5":
            name = _ask_text("Kulüp adı: ")
            club = club_repo.get_by_name(name)
            if club is None:
                _sep()
                print("❌ Kulüp bulunamadı.", flush=True)
                _pause()
                continue

            if not member_names.get(club.name):
                _sep()
                print("ℹ️  Bu kulüpte üye listesi boş. Önce 4 ile ekle.", flush=True)
                _pause()
                continue

            names = _ask_names("Çıkarılacak üyeler: ")
            current = member_names.get(club.name, [])
            to_remove = [n for n in names if n in current]

            if not to_remove:
                _sep()
                print("ℹ️  Bu isimler listede yok, çıkarma yapılmadı.", flush=True)
                _pause()
                continue

            ok = service.remove_member_from_club(club.name, len(to_remove))

            _sep()
            if not ok:
                print("❌ Üye çıkarılamadı.", flush=True)
            else:
                member_names[club.name] = [n for n in current if n not in to_remove]
                updated = club_repo.get_by_name(club.name)
                print(f"✅ {len(to_remove)} üye çıkarıldı. Güncel üye sayısı: {updated.member_count if updated else '?'}", flush=True)
            _pause()
            continue

        if secim == "6":
            name = _ask_text("Kulüp adı: ")
            club = club_repo.get_by_name(name)
            if club is None or club.id is None:
                _sep()
                print("❌ Kulüp bulunamadı.", flush=True)
                _pause()
                continue

            ev = _create_event_interactive(club.id, club.name)
            planned = service.plan_event(ev)

            _sep()
            if planned is None:
                print("❌ Etkinlik planlanamadı (tarih/kapasite/kulüp kontrolü).", flush=True)
            else:
                print(f"✅ Etkinlik eklendi: ID={planned.event_id}", flush=True)
                print(f"{planned.title} | {planned.date.strftime('%d.%m.%Y')} | {planned.location} | Etkinlik türü={planned.event_type}", flush=True)
            _pause()
            continue

        if secim == "7":
            name = _ask_text("Kulüp adı: ")
            events = service.list_events_of_club(name)
            _sep()
            if not events:
                print("❌ Etkinlik bulunamadı.", flush=True)
            else:
                print("✅ Etkinlik listesi:", flush=True)
                _print_event_list(events)
            _pause()
            continue

        if secim == "8":
            t = _ask_text("Etkinlik türü: ")
            events = service.filter_events_by_type(t)
            _sep()
            if not events:
                print(f"❌ Tür filtresi sonucu bulunamadı: {t}", flush=True)
            else:
                print(f"✅ Tür filtresi sonucu: {t}", flush=True)
                _print_event_list(events)
            _pause()
            continue

        if secim == "9":
            start, end = _ask_date_range_days()
            events = service.filter_events_by_date_range(start, end)
            _sep()
            if not events:
                print("❌ Bu tarih aralığında etkinlik bulunamadı.", flush=True)
            else:
                print(f"✅ Aralık: {start.strftime('%d.%m.%Y')} -> {end.strftime('%d.%m.%Y')}", flush=True)
                _print_event_list(events)
            _pause()
            continue
        if secim == "10":
            k = _ask_text("Arama kelimesi: ")
            res = service.search_clubs(k)
            _sep()
            if not res:
                print(f"❌ Arama sonucu bulunamadı: {k}", flush=True)
            else:
                print(f"✅ Arama sonucu: {k}", flush=True)
                _print_club_list(res, member_names)
            _pause()
            continue

        if secim == "11":
            t_input = _ask_text("Tür (Spor Kulübü/Müzik Kulübü/Bilim Kulübü): ").lower()
            t = TYPE_MAP.get(t_input)

            _sep()
        if t is None:
            print("❌ Geçersiz tür. Örnek: Spor Kulübü / Müzik Kulübü / Bilim Kulübü", flush=True)
            _pause()
            continue

        res = service.filter_clubs_by_type(t)
        if not res:
            print(f"❌ Bu türde kulüp bulunamadı: {t_input}", flush=True)
        else:
            print(f"✅ Tür filtresi: {t_input}", flush=True)
            _print_club_list(res, member_names)
            _pause()
            continue


        if secim == "12":
            m = _ask_int("Minimum üye sayısı: ", 0)
            res = service.filter_clubs_by_min_members(m)
            _sep()
            if not res:
                print(f"❌ Min üye filtresi sonucu bulunamadı: {m}", flush=True)
            else:
                print(f"✅ Min üye filtresi: {m}", flush=True)
                _print_club_list(res, member_names)
            _pause()
            continue

        if secim == "13":
            event_id = _ask_int("İptal edilecek etkinlik ID: ", 1)
            ok = service.cancel_event(event_id)
            _sep()
            print("✅ Etkinlik iptal edildi." if ok else "❌ Etkinlik bulunamadı.", flush=True)
            _pause()
            continue

        _sep()
        print("Geçersiz seçim. 0-13 arası bir sayı gir.", flush=True)
        _pause()



# Dosya direkt çalıştırılırsa menüyü açar.
if __name__ == "__main__":
    main()
