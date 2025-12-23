# app/modules/module_4/repository.py

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from app.modules.module_4.base import Club
from app.modules.module_4.implementations import ClubEvent, SportClub, MusicClub, ScienceClub


# Kulüp repo sözleşmesini tanımlayan abstract sınıf.
class ClubRepository(ABC):
    # Kulübü kaydetmeyi zorunlu kılar.
    @abstractmethod
    def add_club(self, club: Club) -> Club:
        pass

    # Tüm kulüpleri listelemeyi zorunlu kılar.
    @abstractmethod
    def list_all(self) -> list[Club]:
        pass

    # Ada göre kulüp bulmayı zorunlu kılar.
    @abstractmethod
    def get_by_name(self, name: str) -> Club | None:
        pass

    # ID'ye göre kulüp bulmayı zorunlu kılar.
    @abstractmethod
    def get_by_id(self, club_id: int) -> Club | None:
        pass

    # Repo için metin normalize eder.
    @staticmethod
    def normalize_name(name: str) -> str:
        return (name or "").strip()

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "ClubRepository":
        raise NotImplementedError("Somut repo bu metodu uygulamalı.")


# Etkinlik repo sözleşmesini tanımlayan abstract sınıf.
class EventRepository(ABC):
    # Etkinlik kaydetmeyi zorunlu kılar.
    @abstractmethod
    def add_event(self, event: ClubEvent) -> ClubEvent:
        pass

    # Tüm etkinlikleri listelemeyi zorunlu kılar.
    @abstractmethod
    def list_all(self) -> list[ClubEvent]:
        pass

    # Kulübe göre etkinlik filtrelemeyi zorunlu kılar.
    @abstractmethod
    def list_by_club(self, club_id: int) -> list[ClubEvent]:
        pass

    # Tarih aralığına göre filtrelemeyi zorunlu kılar.
    @abstractmethod
    def list_by_date_range(self, start: datetime, end: datetime) -> list[ClubEvent]:
        pass

    # Etkinlik türüne göre filtrelemeyi zorunlu kılar.
    @abstractmethod
    def list_by_type(self, event_type: str) -> list[ClubEvent]:
        pass

    # Etkinliği id ile silmeyi zorunlu kılar.
    @abstractmethod
    def remove_by_id(self, event_id: int) -> bool:
        pass

    # Event type normalize eder.
    @staticmethod
    def normalize_type(event_type: str) -> str:
        return (event_type or "").strip().lower()

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "EventRepository":
        raise NotImplementedError("Somut repo bu metodu uygulamalı.")


# RAM üzerinde kulüpleri dict ile tutan repository.
class InMemoryClubRepository(ClubRepository):
    # Boş in-memory repo oluşturur.
    def __init__(self) -> None:
        self.__clubs_by_id: dict[int, Club] = {}
        self.__id_by_name: dict[str, int] = {}
        self.__next_id: int = 1

    # Kulübü kaydeder ve id atar.
    def add_club(self, club: Club) -> Club:
        key = self.normalize_name(club.name)
        if key == "":
            raise ValueError("Kulüp adı boş olamaz.")
        if key in self.__id_by_name:
            raise ValueError("Bu isimde kulüp zaten var.")
        club_id = self.__next_id
        self.__next_id += 1
        club._set_id_internal(club_id)
        self.__clubs_by_id[club_id] = club
        self.__id_by_name[key] = club_id
        return club

    # Tüm kulüpleri listeler.
    def list_all(self) -> list[Club]:
        return list(self.__clubs_by_id.values())

    # Ada göre kulüp bulur.
    def get_by_name(self, name: str) -> Club | None:
        key = self.normalize_name(name)
        if key == "":
            return None
        cid = self.__id_by_name.get(key)
        return self.__clubs_by_id.get(cid) if cid is not None else None

    # ID'ye göre kulüp bulur.
    def get_by_id(self, club_id: int) -> Club | None:
        if not Club.is_positive_int(club_id):
            return None
        return self.__clubs_by_id.get(club_id)

    # Kulübü günceller (üye sayısı gibi değişimler için).
    def update_club(self, club: Club) -> None:
        if club.id is None:
            raise ValueError("Kulübün id'si yok.")
        if club.id not in self.__clubs_by_id:
            raise ValueError("Kulüp bulunamadı.")
        self.__clubs_by_id[club.id] = club
        self.__id_by_name[self.normalize_name(club.name)] = club.id

    # İsim içinde keyword geçen kulüpleri döndürür.
    def search(self, keyword: str) -> list[Club]:
        k = self.normalize_name(keyword).lower()
        if k == "":
            return []
        return [c for c in self.list_all() if k in c.name.lower()]

    # Kulüpleri tür adına göre filtreler.
    def filter_by_type(self, club_type: str) -> list[Club]:
        t = self.normalize_name(club_type)
        if t == "":
            return []
        return [c for c in self.list_all() if c.club_type() == t]

    # Kulüpleri minimum üye sayısına göre filtreler.
    def filter_by_min_members(self, min_members: int) -> list[Club]:
        if not isinstance(min_members, int) or min_members < 0:
            return []
        return [c for c in self.list_all() if c.member_count >= min_members]

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "InMemoryClubRepository":
        return cls()

    # Kulüp adı doğrulaması yapar.
    @staticmethod
    def is_valid_club_name(name: str) -> bool:
        return Club.is_valid_text(name, min_len=2, max_len=60)


# RAM üzerinde etkinlikleri dict ile tutan repository.
class InMemoryEventRepository(EventRepository):
    # Boş in-memory event repo oluşturur.
    def __init__(self) -> None:
        self.__events_by_id: dict[int, ClubEvent] = {}
        self.__ids_by_club: dict[int, list[int]] = {}
        self.__next_id: int = 1

    # Etkinliği kaydeder ve id atar.
    def add_event(self, event: ClubEvent) -> ClubEvent:
        if event.event_id == 0:
            event.event_id = self.__next_id
            self.__next_id += 1
        self.__events_by_id[event.event_id] = event
        self.__ids_by_club.setdefault(event.club_id, []).append(event.event_id)
        return event

    # Tüm etkinlikleri listeler.
    def list_all(self) -> list[ClubEvent]:
        return list(self.__events_by_id.values())

    # Kulüp id’ye göre etkinlikleri listeler.
    def list_by_club(self, club_id: int) -> list[ClubEvent]:
        if not Club.is_positive_int(club_id):
            return []
        ids = self.__ids_by_club.get(club_id, [])
        return [self.__events_by_id[i] for i in ids if i in self.__events_by_id]

    # Tarih aralığına göre etkinlikleri filtreler.
    def list_by_date_range(self, start: datetime, end: datetime) -> list[ClubEvent]:
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            return []
        return [e for e in self.list_all() if start <= e.date <= end]

    # Etkinlik türüne göre etkinlikleri filtreler.
    def list_by_type(self, event_type: str) -> list[ClubEvent]:
        t = self.normalize_type(event_type)
        if t == "":
            return []
        return [e for e in self.list_all() if e.event_type.strip().lower() == t]

    # Event id’ye göre etkinliği siler.
    def remove_by_id(self, event_id: int) -> bool:
        if not Club.is_positive_int(event_id):
            return False
        ev = self.__events_by_id.pop(event_id, None)
        if ev is None:
            return False
        if ev.club_id in self.__ids_by_club:
            self.__ids_by_club[ev.club_id] = [i for i in self.__ids_by_club[ev.club_id] if i != event_id]
        return True

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "InMemoryEventRepository":
        return cls()

    # Gelecek tarih kontrolü yapar.
    @staticmethod
    def is_future(date: datetime) -> bool:
        return isinstance(date, datetime) and date > datetime.now()


# JSON dosya işlemlerini tek yerde toplamak için yardımcı sınıf.
class JsonStorage:
    # Dosya yoksa default döndürerek json okur.
    @staticmethod
    def read(path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            raw = path.read_text(encoding="utf-8")
            if not raw.strip():
                return default
            return json.loads(raw)
        except Exception:
            return default

    # Json veriyi dosyaya yazar ve klasörü garanti eder.
    @staticmethod
    def write(path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ISO string'i datetime'a çevirir.
    @staticmethod
    def parse_dt(value: Any) -> datetime:
        try:
            if isinstance(value, str) and value.strip():
                return datetime.fromisoformat(value)
        except Exception:
            pass
        return datetime.now()

    # Path üretir.
    @classmethod
    def from_str(cls, p: str) -> Path:
        return Path(p)


# JSON dosyada kulüp saklayan repository.
class FileClubRepository(ClubRepository):
    # Kulüpleri saklayacağı json dosya yoluyla repo'yu kurar.
    def __init__(self, file_path: str = "data/module_4/clubs.json") -> None:
        self.__path: Path = Path(file_path)

    # Kulüpleri json'dan okur (dict listesi).
    def _read_all(self) -> list[dict[str, Any]]:
        return JsonStorage.read(self.__path, default=[])

    # Kulüpleri json'a yazar (dict listesi).
    def _write_all(self, items: list[dict[str, Any]]) -> None:
        JsonStorage.write(self.__path, items)

    # Bir sonraki kulüp id'sini üretir.
    def _next_id(self, items: list[dict[str, Any]]) -> int:
        max_id = 0
        for d in items:
            try:
                max_id = max(max_id, int(d.get("id", 0)))
            except Exception:
                continue
        return max_id + 1

    # Kulüp nesnesini json'a uygun dict'e çevirir.
    def _club_to_dict(self, club: Club) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": club.id or 0,
            "type": club.club_type(),
            "name": club.name,
            "description": club.description,
            "member_count": club.member_count,
            "created_at": club.created_at.isoformat(),
        }
        if isinstance(club, SportClub):
            d["sport_name"] = club.sport_name
            d["max_members"] = club.max_members
        if isinstance(club, MusicClub):
            d["instrument_count"] = club.instrument_count
            d["has_studio"] = club.has_studio
        if isinstance(club, ScienceClub):
            d["lab_count"] = club.lab_count
            d["project_based"] = club.project_based
        return d

    # Dict veriden doğru subclass kulübü üretir.
    def _dict_to_club(self, data: dict[str, Any]) -> Club | None:
        t = str(data.get("type", "")).strip()
        name = str(data.get("name", "")).strip()
        desc = str(data.get("description", "")).strip()
        if t == "" or name == "" or desc == "":
            return None

        if t == "SportClub":
            obj = SportClub(name, desc, str(data.get("sport_name", "Basketbol")), int(data.get("max_members", 30)))
        elif t == "MusicClub":
            obj = MusicClub(name, desc, int(data.get("instrument_count", 0)), bool(data.get("has_studio", False)))
        elif t == "ScienceClub":
            obj = ScienceClub(name, desc, int(data.get("lab_count", 0)), bool(data.get("project_based", False)))
        else:
            return None

        club_id = int(data.get("id", 0)) if int(data.get("id", 0)) > 0 else None
        member_count = int(data.get("member_count", 0))
        created_at = JsonStorage.parse_dt(data.get("created_at"))
        return Club.hydrate_base(obj, club_id=club_id, member_count=member_count, created_at=created_at)

    # Kulübü kaydeder ve id atar (json'a yazar).
    def add_club(self, club: Club) -> Club:
        items = self._read_all()
        if any(str(d.get("name", "")).strip() == club.name for d in items):
            raise ValueError("Bu isimde kulüp zaten var.")
        if club.id is None:
            club._set_id_internal(self._next_id(items))
        items.append(self._club_to_dict(club))
        self._write_all(items)
        return club

    # Tüm kulüpleri listeler (json'dan okur).
    def list_all(self) -> list[Club]:
        out: list[Club] = []
        for d in self._read_all():
            c = self._dict_to_club(d)
            if c is not None:
                out.append(c)
        return out

    # Ada göre kulüp bulur (json üstünden).
    def get_by_name(self, name: str) -> Club | None:
        key = self.normalize_name(name)
        if key == "":
            return None
        for d in self._read_all():
            if str(d.get("name", "")).strip() == key:
                return self._dict_to_club(d)
        return None

    # ID’ye göre kulüp bulur (json üstünden).
    def get_by_id(self, club_id: int) -> Club | None:
        if not Club.is_positive_int(club_id):
            return None
        for d in self._read_all():
            if int(d.get("id", 0)) == club_id:
                return self._dict_to_club(d)
        return None

    # Kulübü günceller (json'da id eşleşeni değiştirir).
    def update_club(self, club: Club) -> None:
        if club.id is None:
            raise ValueError("Kulübün id'si yok.")
        items = self._read_all()
        for i, d in enumerate(items):
            if int(d.get("id", 0)) == club.id:
                items[i] = self._club_to_dict(club)
                self._write_all(items)
                return
        raise ValueError("Güncellenecek kulüp bulunamadı.")

    # İsim içinde keyword geçen kulüpleri listeler.
    def search(self, keyword: str) -> list[Club]:
        k = self.normalize_name(keyword).lower()
        if k == "":
            return []
        return [c for c in self.list_all() if k in c.name.lower()]

    # Tür adına göre kulüpleri filtreler.
    def filter_by_type(self, club_type: str) -> list[Club]:
        t = self.normalize_name(club_type)
        if t == "":
            return []
        return [c for c in self.list_all() if c.club_type() == t]

    # Minimum üye sayısına göre kulüpleri filtreler.
    def filter_by_min_members(self, min_members: int) -> list[Club]:
        if not isinstance(min_members, int) or min_members < 0:
            return []
        return [c for c in self.list_all() if c.member_count >= min_members]

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "FileClubRepository":
        return cls()

    # Dosya yolu geçerli mi kontrol eder.
    @staticmethod
    def is_valid_path(file_path: str) -> bool:
        return isinstance(file_path, str) and file_path.strip() != ""


# JSON dosyada etkinlik saklayan repository.
class FileEventRepository(EventRepository):
    # Etkinlikleri saklayacağı json dosya yoluyla repo'yu kurar.
    def __init__(self, file_path: str = "data/module_4/events.json") -> None:
        self.__path: Path = Path(file_path)

    # Eventleri json'dan okur (dict listesi).
    def _read_all(self) -> list[dict[str, Any]]:
        return JsonStorage.read(self.__path, default=[])

    # Eventleri json'a yazar (dict listesi).
    def _write_all(self, items: list[dict[str, Any]]) -> None:
        JsonStorage.write(self.__path, items)

    # Bir sonraki event id'sini üretir.
    def _next_id(self, items: list[dict[str, Any]]) -> int:
        max_id = 0
        for d in items:
            try:
                max_id = max(max_id, int(d.get("event_id", 0)))
            except Exception:
                continue
        return max_id + 1

    # Etkinliği kaydeder ve id atar (json'a yazar).
    def add_event(self, event: ClubEvent) -> ClubEvent:
        items = self._read_all()
        if event.event_id == 0:
            event.event_id = self._next_id(items)
        items.append(event.to_dict())
        self._write_all(items)
        return event

    # Tüm etkinlikleri listeler (json'dan okur).
    def list_all(self) -> list[ClubEvent]:
        return [ClubEvent.from_dict(d) for d in self._read_all()]

    # Kulüp id’ye göre etkinlikleri listeler.
    def list_by_club(self, club_id: int) -> list[ClubEvent]:
        if not Club.is_positive_int(club_id):
            return []
        out: list[ClubEvent] = []
        for d in self._read_all():
            if int(d.get("club_id", 0)) == club_id:
                out.append(ClubEvent.from_dict(d))
        return out

    # Tarih aralığına göre etkinlikleri filtreler.
    def list_by_date_range(self, start: datetime, end: datetime) -> list[ClubEvent]:
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            return []
        return [e for e in self.list_all() if start <= e.date <= end]

    # Etkinlik türüne göre etkinlikleri filtreler.
    def list_by_type(self, event_type: str) -> list[ClubEvent]:
        t = self.normalize_type(event_type)
        if t == "":
            return []
        return [e for e in self.list_all() if e.event_type.strip().lower() == t]

    # Event id’ye göre etkinliği siler.
    def remove_by_id(self, event_id: int) -> bool:
        if not Club.is_positive_int(event_id):
            return False
        items = self._read_all()
        for i, d in enumerate(list(items)):
            if int(d.get("event_id", 0)) == event_id:
                items.pop(i)
                self._write_all(items)
                return True
        return False

    # Boş repo üretir.
    @classmethod
    def empty(cls) -> "FileEventRepository":
        return cls()

    # Dosya var mı kontrol eder.
    @staticmethod
    def file_exists(file_path: str) -> bool:
        return Path(file_path).exists()
