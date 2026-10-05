"""
Database layer (SQLAlchemy 2.x).

Tables
  patients     - patient profile
  assessments  - one run of Symptoms -> Prediction -> Risk -> Recommendation (+ full report JSON)
  predictions  - top-K disease probabilities, linked to patient AND assessment   (Day 2)

Risk level + severity are stored on the assessment row                        (Day 3)
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from app.config import DATABASE_URL

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))  # salted PBKDF2, never plain text
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(10))
    blood_pressure: Mapped[str] = mapped_column(String(10))
    cholesterol: Mapped[str] = mapped_column(String(10))
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    smoking: Mapped[str | None] = mapped_column(String(10), nullable=True)
    physically_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    heavy_drinker: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    conditions: Mapped[str | None] = mapped_column(String(300), nullable=True)
    allergies: Mapped[str | None] = mapped_column(String(300), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")

    def as_profile(self) -> dict:
        return {c: getattr(self, c) for c in
                ["name", "age", "gender", "blood_pressure", "cholesterol", "bmi",
                 "smoking", "physically_active", "heavy_drinker", "conditions", "allergies"]}


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    fever: Mapped[bool] = mapped_column(Boolean, default=False)
    cough: Mapped[bool] = mapped_column(Boolean, default=False)
    fatigue: Mapped[bool] = mapped_column(Boolean, default=False)
    difficulty_breathing: Mapped[bool] = mapped_column(Boolean, default=False)

    severity_level: Mapped[str] = mapped_column(String(10))
    severity_score: Mapped[float] = mapped_column(Float)
    risk_category: Mapped[str] = mapped_column(String(10))
    risk_score: Mapped[float] = mapped_column(Float)
    overall_priority: Mapped[str] = mapped_column(String(10))
    report: Mapped[dict] = mapped_column(JSON)  # full report incl. recommendations

    patient: Mapped[Patient] = relationship(back_populates="assessments")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="assessment", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    disease: Mapped[str] = mapped_column(String(120), index=True)
    probability: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(40))
    severity: Mapped[str] = mapped_column(String(10))

    assessment: Mapped[Assessment] = relationship(back_populates="predictions")


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_assessment(db, patient: Patient, report: dict) -> Assessment:
    """Persist one assessment + its predictions, and stamp ids into the report."""
    s = report["symptoms"]
    a = Assessment(
        patient_id=patient.id,
        fever=s["fever"], cough=s["cough"], fatigue=s["fatigue"],
        difficulty_breathing=s["difficulty_breathing"],
        severity_level=report["severity"]["level"], severity_score=report["severity"]["score"],
        risk_category=report["risk"]["category"], risk_score=report["risk"]["score"],
        overall_priority=report["overall_priority"],
        report=report,
    )
    for p in report["predictions"]:
        a.predictions.append(Prediction(
            patient_id=patient.id, rank=p["rank"], disease=p["disease"],
            probability=p["probability"], category=p["category"], severity=p["severity"]))
    db.add(a)
    db.flush()                       # get a.id
    report["report_id"] = a.id
    report["patient_id"] = patient.id
    a.report = dict(report)          # store a copy that now includes the ids
    flag_modified(a, "report")       # JSON columns don't detect in-place edits -> force UPDATE
    db.commit()
    return a
