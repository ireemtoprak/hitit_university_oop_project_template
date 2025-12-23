# app/modules/module_4/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


# Kulüplerin ortak sözleşmesini (abstract) ve ortak alanlarını tanımlar.
class Club(ABC):
    # Kulübü temel bilgilerle oluşturur ve alanları kapsüller.
    def __init__(self, name: str, description: str, created_at: datetime | None = None) -> None:
        self.__id: int | None = None
        self.__name: str = ""
        self.__description: str = ""
        self.__member_count: int = 0
        self.__created_at: datetime = created_at if created_at is not None else datetime.now()

        self.name = name
        self.description = description

    # Kulübün id bilgisini verir (repo tarafından atanır).
    @property
    def id(self) -> int | None:
        return self.__id

    # Kulübün id bilgisini (yalnız repo içi) ayarlar.
    def _set_id_internal(self, value: int) -> None:
        if not self.is_positive_int(value):
            raise ValueError("id pozitif int olmalıdır.")
        self.__id = value

    # Kulüp adını verir.
    @property
    def name(self) -> str:
        return self.__name

    # Kulüp adını doğrulayarak ayarlar.
    @name.setter
    def name(self, value: str) -> None:
        if not self.is_valid_text(value, min_len=2, max_len=60):
            raise ValueError("name geçersiz.")
        self.__name = value.strip()

    # Kulüp açıklamasını verir.
    @property
    def description(self) -> str:
        return self.__description

    # Kulüp açıklamasını doğrulayarak ayarlar.
    @description.setter
    def description(self, value: str) -> None:
        if not self.is_valid_text(value, min_len=2, max_len=250):
            raise ValueError("description geçersiz.")
        self.__description = value.strip()

    # Kulübün üye sayısını verir.
    @property
    def member_count(self) -> int:
        return self.__member_count

    # Üye sayısını dışarıdan direkt set etmeyi engeller.
    @member_count.setter
    def member_count(self, value: int) -> None:
        raise AttributeError("member_count doğrudan set edilemez; add_member/remove_member kullan.")

    # Üye sayısını kontrollü şekilde (internal) ayarlar.
    def _set_member_count_internal(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("member_count negatif olamaz.")
        self.__member_count = value

    # Kulübün oluşturulma zamanını verir.
    @property
    def created_at(self) -> datetime:
        return self.__created_at

    # created_at alanını internal ayarlar.
    def _set_created_at_internal(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("created_at datetime olmalıdır.")
        self.__created_at = value

    # Kulüp tipini döndürmeyi alt sınıflara zorunlu kılar.
    @abstractmethod
    def club_type(self) -> str:
        pass

    # Üye ekleme davranışını alt sınıflara zorunlu kılar.
    @abstractmethod
    def add_member(self, count: int) -> None:
        pass

    # Üye çıkarma davranışını alt sınıflara zorunlu kılar.
    @abstractmethod
    def remove_member(self, count: int) -> None:
        pass

    # Kulüp bilgisini testlerin kontrol edeceği formatta metne çevirir.
    def get_info(self) -> str:
        return (
            f"name: {self.name}\n"
            f"member_count: {self.member_count}\n"
            f"description: {self.description}\n"
            f"created_at: {self.created_at}\n"
            f"type: {self.club_type()}"
        )

    # Basit metin kontrolü yapar (boş değil, uzunluk aralığı).
    @staticmethod
    def is_valid_text(value: str, min_len: int = 1, max_len: int = 255) -> bool:
        if not isinstance(value, str):
            return False
        s = value.strip()
        if s == "":
            return False
        if len(s) < min_len:
            return False
        if len(s) > max_len:
            return False
        return True

    # Pozitif int kontrolü yapar.
    @staticmethod
    def is_positive_int(value: int) -> bool:
        return isinstance(value, int) and value > 0

    # Base alanları tek seferde doldurur.
    @classmethod
    def hydrate_base(cls, obj: "Club", club_id: int | None, member_count: int, created_at: datetime) -> "Club":
        if club_id is not None:
            obj._set_id_internal(club_id)
        obj._set_member_count_internal(member_count)
        obj._set_created_at_internal(created_at)
        return obj
