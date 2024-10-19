# SQLAlchemy
from sqlalchemy import BigInteger, String, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base model as parent for other models."""
    pass


class Doctors(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=True
    )
    individual_number: Mapped[str] = mapped_column(String(12))

    patients: Mapped[list["Patients"]] = relationship(
        back_populates="doctor", lazy="selectin", 
        cascade="all, delete-orphan"
    )


class Patients(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=True
    )
    individual_number: Mapped[str] = mapped_column(String(12))
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    doctor: Mapped[Doctors] = relationship(
        back_populates="patients", lazy="selectin"
    )

    tests: Mapped[list["PatientTests"]] = relationship(
        back_populates="patient", lazy="selectin",
        cascade="all, delete-orphan"
    )


class PatientTests(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String, nullable=True)
    data: Mapped[dict] = mapped_column(JSON)

    patient: Mapped[Patients] = relationship(
        back_populates="tests", lazy="selectin"
    )
