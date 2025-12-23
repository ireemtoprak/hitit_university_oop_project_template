# app/modules/module_4/implementations.py

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.modules.module_4.base import Club


# Spor kulübü için branş ve kapasite alanlarını ekler.
class SportClub(Club):
    # Spor kulübünü branş ve kapasiteyle kurar.
    def __init__(self, name: str, description: str, sport_name: str, max_members: int, created_at: datetime | None = None) -> None:
        super().__init__(name=name, description=description, created_at=created_at)
        self.__sport_name: str = ""
        self.__max_members: int = 0
        self.sport_name = sport_name
        self.max_members = max_members

    # Spor branş adını verir.
    @property
    def sport_name(self) -> str:
        return self.__sport_name

    # Spor branş adını doğrulayarak ayarlar.
    @sport_name.setter
    def sport_name(self, value: str) -> None:
        if not Club.is_valid_text(value, min_len=2, max_len=40):
            raise ValueError("sport_name geçersiz.")
        self.__sport_name = value.strip()

    # Maksimum üye kapasitesini verir.
    @property
    def max_members(self) -> int:
        return self.__max_members

    # Maksimum üye kapasitesini doğrulayarak ayarlar.
    @max_members.setter
    def max_members(self, value: int) -> None:
        if not Club.is_positive_int(value):
            raise ValueError("max_members pozitif int olmalıdır.")
        self.__max_members = value
        if self.member_count > self.__max_members:
            self._set_member_count_internal(self.__max_members)

    # Bu kulübün tür adını döndürür.
    def club_type(self) -> str:
        return "SportClub"

    # Kulübe üye ekler (kapasiteyi aşarsa eklemez).
    def add_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        if self.member_count + count > self.max_members:
            return
        self._set_member_count_internal(self.member_count + count)

    # Kulüpten üye çıkarır (0 altına düşürmez).
    def remove_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        if self.member_count - count < 0:
            return
        self._set_member_count_internal(self.member_count - count)

    # Spor kulübü için varsayılan event type döndürür.
    @staticmethod
    def default_event_type() -> str:
        return "Sport"

    # Hızlı test/demo için örnek spor kulübü üretir.
    @classmethod
    def ornek_olustur(cls, name: str = "Spor Kulübü") -> "SportClub":
        return cls(name=name, description="Spor etkinlikleri yapılır.", sport_name="Basketbol", max_members=30)


# Müzik kulübü için enstrüman ve stüdyo alanlarını ekler.
class MusicClub(Club):
    # Müzik kulübünü enstrüman sayısı ve stüdyo bilgisiyle kurar.
    def __init__(self, name: str, description: str, instrument_count: int, has_studio: bool, created_at: datetime | None = None) -> None:
        super().__init__(name=name, description=description, created_at=created_at)
        self.__instrument_count: int = 0
        self.__has_studio: bool = False
        self.instrument_count = instrument_count
        self.has_studio = has_studio

    # Enstrüman sayısını verir.
    @property
    def instrument_count(self) -> int:
        return self.__instrument_count

    # Enstrüman sayısını doğrulayarak ayarlar.
    @instrument_count.setter
    def instrument_count(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("instrument_count negatif olamaz.")
        self.__instrument_count = value

    # Stüdyo var mı bilgisini verir.
    @property
    def has_studio(self) -> bool:
        return self.__has_studio

    # Stüdyo var mı bilgisini doğrulayarak ayarlar.
    @has_studio.setter
    def has_studio(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("has_studio bool olmalıdır.")
        self.__has_studio = value

    # Bu kulübün tür adını döndürür.
    def club_type(self) -> str:
        return "MusicClub"

    # Kulübe üye ekler (kapasite sınırı yok).
    def add_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        self._set_member_count_internal(self.member_count + count)

    # Kulüpten üye çıkarır (0 altına düşürmez).
    def remove_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        if self.member_count - count < 0:
            return
        self._set_member_count_internal(self.member_count - count)

    # Müzik kulübü için varsayılan event type döndürür.
    @staticmethod
    def default_event_type() -> str:
        return "Music"

    # Hızlı test/demo için örnek müzik kulübü üretir.
    @classmethod
    def ornek_olustur(cls, name: str = "Müzik Kulübü") -> "MusicClub":
        return cls(name=name, description="Müzik çalışmaları yapılır.", instrument_count=10, has_studio=True)


# Bilim kulübü için laboratuvar ve proje odak alanlarını ekler.
class ScienceClub(Club):
    # Bilim kulübünü lab sayısı ve proje odaklılık bilgisiyle kurar.
    def __init__(self, name: str, description: str, lab_count: int, project_based: bool, created_at: datetime | None = None) -> None:
        super().__init__(name=name, description=description, created_at=created_at)
        self.__lab_count: int = 0
        self.__project_based: bool = False
        self.lab_count = lab_count
        self.project_based = project_based

    # Laboratuvar sayısını verir.
    @property
    def lab_count(self) -> int:
        return self.__lab_count

    # Laboratuvar sayısını doğrulayarak ayarlar.
    @lab_count.setter
    def lab_count(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("lab_count negatif olamaz.")
        self.__lab_count = value

    # Proje odaklı mı bilgisini verir.
    @property
    def project_based(self) -> bool:
        return self.__project_based

    # Proje odaklı mı bilgisini doğrulayarak ayarlar.
    @project_based.setter
    def project_based(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("project_based bool olmalıdır.")
        self.__project_based = value

    # Bu kulübün tür adını döndürür.
    def club_type(self) -> str:
        return "ScienceClub"

    # Kulübe üye ekler.
    def add_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        self._set_member_count_internal(self.member_count + count)

    # Kulüpten üye çıkarır.
    def remove_member(self, count: int) -> None:
        if not Club.is_positive_int(count):
            return
        if self.member_count - count < 0:
            return
        self._set_member_count_internal(self.member_count - count)

    # Bilim kulübü için varsayılan event type döndürür.
    @staticmethod
    def default_event_type() -> str:
        return "Science"

    # Hızlı test/demo için örnek bilim kulübü üretir.
    @classmethod
    def ornek_olustur(cls, name: str = "Bilim Kulübü") -> "ScienceClub":
        return cls(name=name, description="Deney ve proje çalışmaları yapılır.", lab_count=2, project_based=True)


# Etkinlik bilgilerini kapsülleyip kulüple ilişkilendirmek için model sınıfı.
class ClubEvent:
    # Etkinliği temel alanlarla kurar ve kapsüller.
    def __init__(
        self,
        event_id: int = 0,
        club_id: int = 0,
        club_name: str = "",
        title: str = "",
        date: datetime | None = None,
        location: str = "",
        quota: int = 1,
        event_type: str = "General",
    ) -> None:
        self.__event_id: int = 0
        self.__club_id: int = 0
        self.__club_name: str = ""
        self.__title: str = ""
        self.__date: datetime = datetime.now()
        self.__location: str = ""
        self.__quota: int = 1
        self.__event_type: str = "General"

        self.event_id = event_id
        self.club_id = club_id
        self.club_name = club_name
        self.title = title
        self.date = date if date is not None else datetime.now()
        self.location = location
        self.quota = quota
        self.event_type = event_type

    # Event id bilgisini verir.
    @property
    def event_id(self) -> int:
        return self.__event_id

    # Event id bilgisini ayarlar (0 ise repo otomatik atar).
    @event_id.setter
    def event_id(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("event_id 0 veya pozitif int olmalıdır.")
        self.__event_id = value

    # Kulüp id bilgisini verir.
    @property
    def club_id(self) -> int:
        return self.__club_id

    # Kulüp id bilgisini ayarlar.
    @club_id.setter
    def club_id(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("club_id 0 veya pozitif int olmalıdır.")
        self.__club_id = value

    # Kulüp adını verir.
    @property
    def club_name(self) -> str:
        return self.__club_name

    # Kulüp adını doğrulayarak ayarlar.
    @club_name.setter
    def club_name(self, value: str) -> None:
        if value == "":
            self.__club_name = ""
            return
        if not Club.is_valid_text(value, min_len=2, max_len=60):
            raise ValueError("club_name geçersiz.")
        self.__club_name = value.strip()

    # Etkinlik başlığını verir.
    @property
    def title(self) -> str:
        return self.__title

    # Etkinlik başlığını doğrulayarak ayarlar.
    @title.setter
    def title(self, value: str) -> None:
        if value == "":
            self.__title = ""
            return
        if not Club.is_valid_text(value, min_len=2, max_len=80):
            raise ValueError("title geçersiz.")
        self.__title = value.strip()

    # Etkinlik tarihini verir.
    @property
    def date(self) -> datetime:
        return self.__date

    # Etkinlik tarihini doğrulayarak ayarlar.
    @date.setter
    def date(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("date datetime olmalıdır.")
        self.__date = value

    # Etkinlik yerini verir.
    @property
    def location(self) -> str:
        return self.__location

    # Etkinlik yerini doğrulayarak ayarlar.
    @location.setter
    def location(self, value: str) -> None:
        if value == "":
            self.__location = ""
            return
        if not Club.is_valid_text(value, min_len=2, max_len=80):
            raise ValueError("location geçersiz.")
        self.__location = value.strip()

    # Kontenjan bilgisini verir.
    @property
    def quota(self) -> int:
        return self.__quota

    # Kontenjan bilgisini doğrulayarak ayarlar.
    @quota.setter
    def quota(self, value: int) -> None:
        if not self.is_valid_quota(value):
            raise ValueError("quota pozitif int olmalıdır.")
        self.__quota = value

    # Etkinlik türünü verir.
    @property
    def event_type(self) -> str:
        return self.__event_type

    # Etkinlik türünü doğrulayarak ayarlar.
    @event_type.setter
    def event_type(self, value: str) -> None:
        if not isinstance(value, str) or value.strip() == "":
            self.__event_type = "General"
            return
        self.__event_type = value.strip()

    # Event'i dict formatına çevirir (repo/file için).
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "club_id": self.club_id,
            "club_name": self.club_name,
            "title": self.title,
            "date": self.date.isoformat(),
            "location": self.location,
            "quota": self.quota,
            "event_type": self.event_type,
        }

    # Dict içinden event üretir (repo/file için).
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClubEvent":
        dt = datetime.fromisoformat(str(data.get("date"))) if data.get("date") else datetime.now()
        return cls(
            event_id=int(data.get("event_id", 0)),
            club_id=int(data.get("club_id", 0)),
            club_name=str(data.get("club_name", "")),
            title=str(data.get("title", "")),
            date=dt,
            location=str(data.get("location", "")),
            quota=int(data.get("quota", 1)),
            event_type=str(data.get("event_type", "General")),
        )

    # Kontenjan için doğrulama yapar.
    @staticmethod
    def is_valid_quota(value: int) -> bool:
        return isinstance(value, int) and value > 0

    # Hızlı test/demo için örnek event üretir.
    @classmethod
    def ornek_olustur(cls, club_id: int, club_name: str) -> "ClubEvent":
        return cls(
            event_id=0,
            club_id=club_id,
            club_name=club_name,
            title="Örnek Etkinlik",
            date=datetime.now(),
            location="Kampüs",
            quota=10,
            event_type="General",
        )
