# app/modules/module_4/repository.py

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Iterable


class InMemoryClubRepository:

    def __init__(self) -> None:
        # Kulüpleri isimle hızlı bulmak için RAM’de sözlük olarak saklar
        self._clubs_by_name: Dict[str, Any] = {}

    def add_club(self, club: Any) -> None:
        # Kulübü ekler; boş/isim yoksa veya aynı isim varsa hata verir
        if club is None or getattr(club, "name", None) is None:
            raise ValueError("Kulüp boş olamaz.")

        if club.name in self._clubs_by_name:
            raise ValueError("Bu isimde kulüp zaten var.")

        self._clubs_by_name[club.name] = club

    def list_all(self) -> List[Any]:
        # RAM’deki tüm kulüp nesnelerini liste olarak döndürür
        return list(self._clubs_by_name.values())

    def get_by_name(self, club_name: str) -> Optional[Any]:
        # Kulüp adından tek bir kulübü bulur; yoksa None döndürür
        return self._clubs_by_name.get(club_name)

    def search(self, keyword: str) -> List[Any]:
        # Anahtar kelime kulüp adının içinde geçiyorsa eşleşenleri döndürür
        if keyword is None:
            return []
        k = keyword.strip().lower()
        if not k:
            return []
        return [c for c in self.list_all() if k in c.name.lower()]


class InMemoryEventRepository:

    def __init__(self) -> None:
        # Etkinlikleri RAM’de listede tutar ve otomatik ID sayacı başlatır
        self._events: List[Any] = []
        self._next_id: int = 1

    def add_event(self, event: Any) -> Any:
        # Etkinliği ekler; ID yoksa sıradaki ID’yi verip kaydeder
        if getattr(event, "event_id", None) in (None, 0):
            event.event_id = self._next_id
            self._next_id += 1
        self._events.append(event)
        return event

    def list_all(self) -> List[Any]:
        # RAM’deki tüm etkinlikleri liste olarak döndürür
        return list(self._events)

    def list_by_club(self, club_name: str) -> List[Any]:
        # Verilen kulüp adına ait etkinlikleri filtreleyip döndürür
        if club_name is None:
            return []
        return [e for e in self._events if e.club_name == club_name]

    @staticmethod
    def is_future_date(date: datetime) -> bool:
        # Verilen tarihin şu andan ileri bir zaman olup olmadığını kontrol eder
        if date is None:
            return False
        return date > datetime.now()

    @classmethod
    def create_with_seed(cls, seed_events: Iterable[Any]) -> "InMemoryEventRepository":
        # Başlangıç etkinlikleriyle dolu bir repository üretir (test/demo için)
        repo = cls()
        for ev in seed_events:
            repo.add_event(ev)
        return repo
    
# Verileri RAM yerine dosyada saklamak için
# Böylece program kapanıp açılsa bile kayıtlar durur.


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
        # Dosya yolunun klasörü yoksa oluşturur, varsa sorun çıkarmaz
        file_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_json(file_path: Path, default: Any) -> Any:
        # JSON dosyasını okur; dosya yok/boş/bozuksa default döndürür
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
        # Veriyi JSON’a çevirip dosyaya yazar (Türkçe bozulmasın diye UTF-8)
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
        # Kulüp kayıtlarının tutulacağı JSON dosya yolunu ayarlar
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
       # Dosyadan gelen dict’i type bilgisine göre doğru kulüp nesnesine çevirir.
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
        # Kulüp JSON dosyasındaki tüm kayıtları dict listesi olarak okur
        return JsonStorageHelper.read_json(self._path, default=[])

    def _write_all_dicts(self, clubs_list: List[Dict[str, Any]]) -> None:
        # Kulüp dict listesini JSON dosyasına topluca yazar
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
        # Dosyada ada göre kulübü bulup nesne döndürür; yoksa None
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
        # Anahtar kelimeye göre kulüp adlarında arama yapıp eşleşenleri döndürür
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
        # Anahtar kelimeye göre kulüp adlarında arama yapıp eşleşenleri döndürür
        self._path = Path(file_path)

    def _read_all(self) -> List[Dict[str, Any]]:
        # Event JSON dosyasındaki tüm kayıtları dict listesi olarak okur
        return JsonStorageHelper.read_json(self._path, default=[])

    def _write_all(self, items: List[Dict[str, Any]]) -> None:
        # Event dict listesini JSON dosyasına topluca yazar 
        JsonStorageHelper.write_json(self._path, items)

    def _next_id(self, items: List[Dict[str, Any]]) -> int:
        # Dosyadaki en büyük event_id’yi bulup bir sonrakini üretir.
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
        # Event’i dosyaya ekler; ID yoksa otomatik ID atar ve kaydeder
        items = self._read_all()

        if getattr(event, "event_id", 0) in (0, None):
            new_id = self._next_id(items)
            event.event_id = new_id

        items.append(self._event_to_dict(event))
        self._write_all(items)
        return event

    def list_by_club(self, club_name: str, event_class: Any) -> List[Any]:
        # Belirli kulübün event’lerini dosyadan okuyup nesne listesi döndürür
        out: List[Any] = []
        for d in self._read_all():
            if d.get("club_name") == club_name:
                out.append(self._dict_to_event(d, event_class))
        return out

    def list_all(self, event_class: Any) -> List[Any]:
        # Dosyadaki tüm event’leri nesne listesi olarak döndürür
        return [self._dict_to_event(d, event_class) for d in self._read_all()]
    
   

from datetime import datetime


def _im_club_get_by_id(self, club_id: int):
    # Kulübü eklenme sırasını ID kabul ederek ID ile döndürür
    if not isinstance(club_id, int) or club_id <= 0:
        return None
    clubs = self.list_all()  # eklenme sırasını dict korur
    idx = club_id - 1
    if 0 <= idx < len(clubs):
        return clubs[idx]
    return None


def _im_club_filter_by_type(self, club_type: str):
    # Kulüpleri türüne göre (SportClub, MusicClub, ScienceClub) filtreler
    t = (club_type or "").strip()
    if not t:
        return []
    out = []
    for c in self.list_all():
        try:
            if c.club_type() == t:
                out.append(c)
        except Exception:
            continue
    return out


def _im_club_filter_by_min_members(self, min_members: int):
    # Üye sayısı verilen değerden büyük veya eşit olan kulüpleri döndürür
    if not isinstance(min_members, int) or min_members < 0:
        return []
    return [c for c in self.list_all() if getattr(c, "member_count", 0) >= min_members]


# Metotları sınıfa ekle 
InMemoryClubRepository.get_by_id = _im_club_get_by_id
InMemoryClubRepository.filter_by_type = _im_club_filter_by_type
InMemoryClubRepository.filter_by_min_members = _im_club_filter_by_min_members


def _im_event_list_by_date_range(self, start: datetime, end: datetime):
    # Etkinlikleri verilen başlangıç ve bitiş tarihine göre filtreler
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        return []
    out = []
    for e in self.list_all():
        d = getattr(e, "date", None)
        if isinstance(d, datetime) and start <= d <= end:
            out.append(e)
    return out


def _im_event_list_by_type(self, event_type: str):
    # Etkinlikleri event_type alanına göre filtreler
    t = (event_type or "").strip().lower()
    if not t:
        return []
    out = []
    for e in self.list_all():
        et = str(getattr(e, "event_type", "")).strip().lower()
        if et == t:
            out.append(e)
    return out


def _im_event_remove_by_id(self, event_id: int) -> bool:
   # Event ID’ye göre etkinliği listeden siler
    if not isinstance(event_id, int):
        return False
    for i, e in enumerate(list(self._events)):
        if getattr(e, "event_id", None) == event_id:
            self._events.pop(i)
            return True
    return False


InMemoryEventRepository.list_by_date_range = _im_event_list_by_date_range
InMemoryEventRepository.list_by_type = _im_event_list_by_type
InMemoryEventRepository.remove_by_id = _im_event_remove_by_id


def _file_club_get_by_id(self, club_id: int, factory: Any):
   # Dosyadaki kayıt sırasını ID kabul ederek kulübü ID ile döndürür
    if not isinstance(club_id, int) or club_id <= 0:
        return None
    all_dicts = self._read_all_dicts()
    idx = club_id - 1
    if 0 <= idx < len(all_dicts):
        return self._dict_to_club(all_dicts[idx], factory)
    return None


def _file_club_filter_by_type(self, club_type: str, factory: Any):
    # Dosyadaki kulüpleri türüne göre filtreleyip döndürür
    t = (club_type or "").strip()
    if not t:
        return []
    out = []
    for c in self.list_all(factory=factory):
        try:
            if c.club_type() == t:
                out.append(c)
        except Exception:
            continue
    return out


def _file_club_filter_by_min_members(self, min_members: int, factory: Any):
    # Dosyadaki kulüpleri minimum üye sayısına göre filtreler
    if not isinstance(min_members, int) or min_members < 0:
        return []
    return [c for c in self.list_all(factory=factory) if getattr(c, "member_count", 0) >= min_members]


FileClubRepository.get_by_id = _file_club_get_by_id
FileClubRepository.filter_by_type = _file_club_filter_by_type
FileClubRepository.filter_by_min_members = _file_club_filter_by_min_members


def _file_event_list_by_date_range(self, start: datetime, end: datetime, event_class: Any):
        # Dosyadaki etkinlikleri tarih aralığına göre filtreler
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        return []
    out = []
    for ev in self.list_all(event_class=event_class):
        d = getattr(ev, "date", None)
        if isinstance(d, datetime) and start <= d <= end:
            out.append(ev)
    return out


def _file_event_list_by_type(self, event_type: str, event_class: Any):
    # Dosyadaki etkinlikleri türüne göre filtreleyip döndürür
    t = (event_type or "").strip().lower()
    if not t:
        return []
    out = []
    for ev in self.list_all(event_class=event_class):
        et = str(getattr(ev, "event_type", "")).strip().lower()
        if et == t:
            out.append(ev)
    return out


def _file_event_remove_by_id(self, event_id: int) -> bool:
    # Event ID’ye göre etkinliği dosyadan siler
    if not isinstance(event_id, int):
        return False
    items = self._read_all()
    for i, d in enumerate(list(items)):
        try:
            if int(d.get("event_id", 0)) == event_id:
                items.pop(i)
                self._write_all(items)
                return True
        except Exception:
            continue
    return False


FileEventRepository.list_by_date_range = _file_event_list_by_date_range
FileEventRepository.list_by_type = _file_event_list_by_type
FileEventRepository.remove_by_id = _file_event_remove_by_id


