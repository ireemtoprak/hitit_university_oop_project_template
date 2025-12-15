# app/modules/module_4/base.py

from abc import ABC, abstractmethod
from datetime import datetime


class Club(ABC):
    """Club modülündeki tüm kulüpler için base class"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.member_count = 0
        self.description = description
        self.created_at = datetime.now()

    @abstractmethod
    def add_member(self, count: int) -> None:
        """Kulübe üye ekleme (subclass override edecek)."""
        pass

    @abstractmethod
    def remove_member(self, count: int) -> None:
        """Kulüpten üye çıkarma davranışı (subclass override edecek)."""
        pass

    @abstractmethod
    def club_type(self) -> str:
        """Kulüp türünü döndürür (SportClub, MusicClub, ScienceClub/ArtClub gibi)."""
        pass

    def get_info(self) -> str:
        """Testlerde kontrol edilecek bilgi metnini döndürür."""
        return (
            f"name: {self.name}\n"
            f"member_count: {self.member_count}\n"
            f"description: {self.description}\n"
            f"created_at: {self.created_at}\n"
            f"type: {self.club_type()}"
        )
