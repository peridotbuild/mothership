import pydantic
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(
    MappedAsDataclass,
    DeclarativeBase,
    dataclass_callable=pydantic.dataclasses.dataclass,
):
    pass
