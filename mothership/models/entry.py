from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from mothership.models import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    entry_uuid: Mapped[str] = mapped_column(nullable=False)
    package_name: Mapped[str] = mapped_column(nullable=False)
    package_version: Mapped[str] = mapped_column(nullable=False)
    package_release: Mapped[str] = mapped_column(nullable=False)
    package_epoch: Mapped[str] = mapped_column(nullable=False)
    os_release: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"Entry(id={self.id}, entry_uuid={self.entry_uuid}, package_name={self.package_name}, package_version={self.package_version}, package_release={self.package_release}, package_epoch={self.package_epoch})"
