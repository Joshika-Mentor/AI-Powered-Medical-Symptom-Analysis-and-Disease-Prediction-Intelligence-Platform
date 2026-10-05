"""
FastAPI app  -  run with:   uvicorn app.main:app --reload
Interactive docs:           http://127.0.0.1:8000/docs
Dashboard:                  http://127.0.0.1:8000/dashboard
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import check_pw, current_user, hash_pw, make_token
from app.db import Assessment, Patient, User, get_db, init_db, save_assessment
from app.schemas import AssessIn, ChatIn, LoginIn, PatientIn, RegisterIn, SymptomsIn
from app.services import analytics, chat, predictor, risk
from app.services.assessment import run_assessment
from app.services.reports import report_to_pdf, report_to_xlsx

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    predictor.model_info()   # warm up: load models once at start-up (fast first request)
    risk.risk_model_info()
    yield


app = FastAPI(title="MedAssist AI",
              version="1.0.0", lifespan=lifespan)


# ------------------------------------------------------------------ helpers ---------
def _get_patient(db: Session, patient_id: int) -> Patient:
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, f"Patient {patient_id} not found")
    return p


def _get_report(db: Session, patient_id: int, assessment_id: int | None) -> dict:
    _get_patient(db, patient_id)
    q = select(Assessment).where(Assessment.patient_id == patient_id)
    if assessment_id:
        q = q.where(Assessment.id == assessment_id)
    a = db.scalars(q.order_by(Assessment.id.desc())).first()
    if not a:
        raise HTTPException(404, "No assessment found for this patient - POST symptoms first")
    return a.report


# ------------------------------------------------------------------ basics ----------
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/dashboard")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model/info")
def model_info():
    return {"disease_model": predictor.model_info(), "risk_model": risk.risk_model_info()}


# ------------------------------------------------------------------ patients --------
@app.post("/patients", status_code=201)
def create_patient(body: PatientIn, db: Session = Depends(get_db)):
    p = Patient(**body.model_dump())
    db.add(p)
    db.commit()
    return {"id": p.id, **p.as_profile()}


@app.get("/patients")
def list_patients(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    rows = db.scalars(select(Patient).order_by(Patient.id.desc()).limit(limit)).all()
    return [{"id": p.id, **p.as_profile()} for p in rows]


@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = _get_patient(db, patient_id)
    return {"id": p.id, **p.as_profile(), "assessments": [a.id for a in p.assessments]}


# ------------------------------------------------------------------ assessment ------
@app.post("/patients/{patient_id}/assessments", status_code=201)
def assess_existing_patient(patient_id: int, symptoms: SymptomsIn, db: Session = Depends(get_db)):
    """Day 2-5: symptoms -> disease probabilities -> severity -> risk -> recommendations (all saved)."""
    p = _get_patient(db, patient_id)
    report = run_assessment(p.as_profile(), symptoms.model_dump())
    save_assessment(db, p, report)
    return report


@app.post("/assess", status_code=201)
def assess_new_patient(body: AssessIn, db: Session = Depends(get_db)):
    """One-shot demo endpoint: create patient + run full pipeline."""
    p = Patient(**body.patient.model_dump())
    db.add(p)
    db.commit()
    report = run_assessment(p.as_profile(), body.symptoms.model_dump(), body.red_flags)
    save_assessment(db, p, report)
    return report


# ------------------------------------------------------------------ reports ---------
@app.get("/patients/{patient_id}/report")
def report_json(patient_id: int, assessment_id: int | None = None, db: Session = Depends(get_db)):
    return _get_report(db, patient_id, assessment_id)


@app.get("/patients/{patient_id}/report/pdf")
def report_pdf(patient_id: int, assessment_id: int | None = None, db: Session = Depends(get_db)):
    r = _get_report(db, patient_id, assessment_id)
    return Response(report_to_pdf(r), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="health_report_{patient_id}.pdf"'})


@app.get("/patients/{patient_id}/report/excel")
def report_excel(patient_id: int, assessment_id: int | None = None, db: Session = Depends(get_db)):
    r = _get_report(db, patient_id, assessment_id)
    return Response(
        report_to_xlsx(r),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="health_report_{patient_id}.xlsx"'})


# ------------------------------------------------------------------ analytics -------
@app.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    return analytics.build_summary(db)


# ------------------------------------------------------------------ accounts -------
@app.post("/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    u = User(name=body.name.strip(), email=email, password_hash=hash_pw(body.password))
    db.add(u)
    db.commit()
    return {"token": make_token(u.id), "name": u.name}


@app.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == body.email.lower().strip()))
    if not u or not check_pw(body.password, u.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"token": make_token(u.id), "name": u.name}


def _own_assessment(db: Session, user: User, aid: int) -> Assessment:
    a = db.get(Assessment, aid)
    if not a or a.patient.user_id != user.id:
        raise HTTPException(404, "Report not found")
    return a


@app.post("/assessment", status_code=201)
def my_assessment(body: AssessIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Signed-in flow: save/update my profile, run the full pipeline, store the result."""
    p = db.scalar(select(Patient).where(Patient.user_id == user.id))
    if p:
        for k, v in body.patient.model_dump().items():
            setattr(p, k, v)
    else:
        p = Patient(**body.patient.model_dump(), user_id=user.id)
        db.add(p)
    db.commit()
    report = run_assessment(p.as_profile(), body.symptoms.model_dump(), body.red_flags)
    save_assessment(db, p, report)
    return report


@app.get("/reports")
def my_reports(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Assessment).join(Patient).where(Patient.user_id == user.id)
                      .order_by(Assessment.id.desc())).all()
    out = []
    for a in rows:
        top = a.predictions[0] if a.predictions else None
        out.append({"id": a.id, "date": a.created_at.isoformat(), "top_disease": top.disease if top else "-",
                    "probability": round(top.probability * 100, 1) if top else 0, "severity": a.severity_level,
                    "risk": a.risk_category, "risk_score": a.risk_score, "priority": a.overall_priority,
                    "emergency": a.report.get("emergency", {}).get("flag", False)})
    return out


@app.get("/report/{assessment_id}")
def my_report(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _own_assessment(db, user, assessment_id).report


@app.get("/report/{assessment_id}/pdf")
def my_report_pdf(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own_assessment(db, user, assessment_id)
    return Response(report_to_pdf(a.report), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="MedAssist_report_{a.id}.pdf"'})


@app.get("/report/{assessment_id}/excel")
def my_report_excel(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own_assessment(db, user, assessment_id)
    return Response(report_to_xlsx(a.report),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="MedAssist_report_{a.id}.xlsx"'})


@app.post("/chat")
def chat_endpoint(body: ChatIn, db: Session = Depends(get_db)):
    """'Ask MedAssist AI' assistant: safety check -> quick symptom check / disease info / platform questions."""
    return chat.answer(body.message, db)


@app.get("/assessment", include_in_schema=False)
def assessment_page():
    return RedirectResponse("/dashboard#new")


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC / "dashboard.html")
