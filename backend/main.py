from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from sqlmodel import Session, SQLModel

from .database import engine, get_session
from .models import HSC, SSLC


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="School Result Organizing Microservice", lifespan=lifespan)


# --- AUTH ENDPOINT ---
@app.post("/api/login")
def login():
    # TODO: Implement login verification logic
    return {"message": "Login successful stub"}


# --- SSLC ENDPOINTS ---
@app.get("/sslc/classwise")
def get_sslc_classwise(class_name: str, session: Session = Depends(get_session)):
    # TODO: Get students filtered by class
    pass


@app.get("/sslc/toppers")
def get_sslc_toppers(limit: int = 10, session: Session = Depends(get_session)):
    # TODO: Get overall top students based on total marks
    pass


@app.get("/sslc/subject/toppers")
def get_sslc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    # TODO: Get subject-specific toppers
    pass


# --- HSC ENDPOINTS ---
@app.get("/hsc/groupwise")
def get_hsc_groupwise(group_name: str, session: Session = Depends(get_session)):
    # TODO: Get students filtered by academic group split
    pass


@app.get("/hsc/classwise")
def get_hsc_classwise(class_name: str, session: Session = Depends(get_session)):
    # TODO: Get students filtered by class
    pass


@app.get("/hsc/toppers")
def get_hsc_toppers(limit: int = 10, session: Session = Depends(get_session)):
    # TODO: Get overall top students based on total marks or cut-off
    pass


@app.get("/hsc/subject/toppers")
def get_hsc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    # TODO: Get subject-specific toppers
    pass
