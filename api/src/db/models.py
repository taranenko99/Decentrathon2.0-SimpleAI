# SQL
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base model as parent for other models."""
    pass
