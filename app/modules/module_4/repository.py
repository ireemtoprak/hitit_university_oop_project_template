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
    
# Verileri RAM yerine dosyada saklamak için
# Böylece program kapanıp açılsa bile kayıtlar durur.

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class JsonStorageHelper:
    """
    Öğrenci işi basit JSON yardımcı sınıf.
    Repository'lerde tekrar eden okuma/yazma işini azaltmak için yaptım.
    """

    @staticmethod
    def ensure_parent_dir(file_path: Path) -> None:
        # Dosyanın klasörü yoksa oluştur.
        file_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_json(file_path: Path, default: Any) -> Any:
        # Dosya yoksa default dön.
        if not file_path.exists():
            return default

        # Boş dosya olursa hata çıkmasın diye try/except.
        try:
            text = file_path.read_text(encoding="utf-8")
            if not text.strip():
                return default
            return json.loads(text)
        except Exception:
            return default

    @staticmethod
    def write_json(file_path: Path, data: Any) -> None:
        JsonStorageHelper.ensure_parent_dir(file_path)
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class FileClubRepository:
    """
    Kulüp verilerini JSON dosyada saklayan repository.
    Veriler program kapansa bile kaybolmasın diye
    """

    def __init__(self, file_path: str = "data/module_4/clubs.json") -> None:
        self._path = Path(file_path)

    def _club_to_dict(self, club: Any) -> Dict[str, Any]:
        # Kulüp nesnesini JSON'a uygun dict'e çevirmek için
        tip = club.__class__.__name__

        base = {
            "type": tip,
            "name": club.name,
            "description": club.description,
            "member_count": club.member_count,
            "created_at": club.created_at.isoformat() if hasattr(club, "created_at") else datetime.now().isoformat(),
        }

        # Type'a göre ek alanlar
        if hasattr(club, "sport_name"):
            base["sport_name"] = club.sport_name
        if hasattr(club, "max_members"):
            base["max_members"] = club.max_members

        if hasattr(club, "instrument_count"):
            base["instrument_count"] = club.instrument_count
        if hasattr(club, "has_studio"):
            base["has_studio"] = club.has_studio

        if hasattr(club, "lab_count"):
            base["lab_count"] = club.lab_count
        if hasattr(club, "project_based"):
            base["project_based"] = club.project_based

        return base

    def _dict_to_club(self, data: Dict[str, Any], factory: Any) -> Any:
        """
        Dict -> kulüp nesnesi.
        Burada 'factory' parametresi ile implementations içindeki sınıflara erişiyoruz.
        factory içinde şu isimler olmalı:
          SportClub, MusicClub, ScienceClub
        """
        tip = data.get("type")
        name = data.get("name")
        description = data.get("description")

        # Base alanlar kontrol
        if not tip or not name or description is None:
            return None

        # Type'a göre nesne oluştur
        if tip == "SportClub":
            obj = factory.SportClub(
                name,
                description,
                data.get("sport_name", ""),
                int(data.get("max_members", 0)),
            )
        elif tip == "MusicClub":
            obj = factory.MusicClub(
                name,
                description,
                int(data.get("instrument_count", 0)),
                bool(data.get("has_studio", False)),
            )
        elif tip == "ScienceClub":
            obj = factory.ScienceClub(
                name,
                description,
                int(data.get("lab_count", 0)),
                bool(data.get("project_based", False)),
            )
        else:
            # Bilinmeyen tip -> atla
            return None

        # Kayıtlı member_count / created_at geri yükle
        try:
            obj.member_count = int(data.get("member_count", 0))
        except Exception:
            obj.member_count = 0

        try:
            created_str = data.get("created_at")
            obj.created_at = datetime.fromisoformat(created_str) if created_str else datetime.now()
        except Exception:
            obj.created_at = datetime.now()

        return obj

    def _read_all_dicts(self) -> List[Dict[str, Any]]:
        return JsonStorageHelper.read_json(self._path, default=[])

    def _write_all_dicts(self, clubs_list: List[Dict[str, Any]]) -> None:
        JsonStorageHelper.write_json(self._path, clubs_list)

    def add_club(self, club: Any) -> None:
        # Aynı isimli kulüp eklenmesin
        all_data = self._read_all_dicts()
        if any(x.get("name") == club.name for x in all_data):
            raise ValueError("Bu isimde kulüp zaten var (file repo).")

        all_data.append(self._club_to_dict(club))
        self._write_all_dicts(all_data)

    def list_all(self, factory: Any) -> List[Any]:
        # factory: implementations modülü
        out: List[Any] = []
        for d in self._read_all_dicts():
            club_obj = self._dict_to_club(d, factory)
            if club_obj is not None:
                out.append(club_obj)
        return out

    def get_by_name(self, club_name: str, factory: Any) -> Optional[Any]:
        for d in self._read_all_dicts():
            if d.get("name") == club_name:
                return self._dict_to_club(d, factory)
        return None

    def update_club(self, club: Any) -> None:
        # Üye sayısı değişince vs. kaydetmek için.
        all_data = self._read_all_dicts()
        for i, d in enumerate(all_data):
            if d.get("name") == club.name:
                all_data[i] = self._club_to_dict(club)
                self._write_all_dicts(all_data)
                return
        raise ValueError("Güncellenecek kulüp bulunamadı (file repo).")

    def search(self, keyword: str, factory: Any) -> List[Any]:
        k = (keyword or "").strip().lower()
        if not k:
            return []
        result: List[Any] = []
        for club in self.list_all(factory):
            if k in club.name.lower():
                result.append(club)
        return result


class FileEventRepository:
    """
    Etkinlik verilerini JSON dosyada saklayan repository.
    Program kapansa bile etkinlikler kaybolmaz.
    """


    def __init__(self, file_path: str = "data/module_4/events.json") -> None:
        self._path = Path(file_path)

    def _read_all(self) -> List[Dict[str, Any]]:
        return JsonStorageHelper.read_json(self._path, default=[])

    def _write_all(self, items: List[Dict[str, Any]]) -> None:
        JsonStorageHelper.write_json(self._path, items)

    def _next_id(self, items: List[Dict[str, Any]]) -> int:
        # Basit ID üretimi: max + 1
        max_id = 0
        for d in items:
            try:
                max_id = max(max_id, int(d.get("event_id", 0)))
            except Exception:
                continue
        return max_id + 1

    def _event_to_dict(self, event: Any) -> Dict[str, Any]:
        # dataclass ise asdict ile daha kolay
        if is_dataclass(event):
            d = asdict(event)
        else:
            d = {
                "event_id": getattr(event, "event_id", 0),
                "club_name": getattr(event, "club_name", ""),
                "title": getattr(event, "title", ""),
                "date": getattr(event, "date", datetime.now()),
                "location": getattr(event, "location", ""),
                "quota": getattr(event, "quota", 0),
                "event_type": getattr(event, "event_type", "General"),
            }

        # date datetime ise isoformat'a çevir
        if isinstance(d.get("date"), datetime):
            d["date"] = d["date"].isoformat()

        return d

    def _dict_to_event(self, data: Dict[str, Any], event_class: Any) -> Any:
        # event_class: implementations içindeki ClubEvent
        try:
            date_str = data.get("date")
            dt = datetime.fromisoformat(date_str) if date_str else datetime.now()
        except Exception:
            dt = datetime.now()

        return event_class(
            event_id=int(data.get("event_id", 0)),
            club_name=str(data.get("club_name", "")),
            title=str(data.get("title", "")),
            date=dt,
            location=str(data.get("location", "")),
            quota=int(data.get("quota", 0)),
            event_type=str(data.get("event_type", "General")),
        )

    def add_event(self, event: Any) -> Any:
        items = self._read_all()

        # event_id 0 ise otomatik ver
        if getattr(event, "event_id", 0) in (0, None):
            new_id = self._next_id(items)
            event.event_id = new_id

        items.append(self._event_to_dict(event))
        self._write_all(items)
        return event

    def list_by_club(self, club_name: str, event_class: Any) -> List[Any]:
        out: List[Any] = []
        for d in self._read_all():
            if d.get("club_name") == club_name:
                out.append(self._dict_to_event(d, event_class))
        return out

    def list_all(self, event_class: Any) -> List[Any]:
        return [self._dict_to_event(d, event_class) for d in self._read_all()]

