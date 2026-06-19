import csv
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any, List, Optional

from DTOs import (
    GroupDTO,
    GroupwiseResponseDTO,
    HSCFailureResponse,
    HSCStudentDataResponse,
    HSCStudentForm,
    SectionDTO,
    SSLCClasswiseResponseDTO,
    SSLCFailureResponse,
    SSLCStudentDataResponse,
    SSLCStudentForm,
    SSLCTopperResponse,
    StudentGroupwiseDTO,
    ExamResultSummaryDTO,
    ResultsSummaryDTO,
    StudentSubmitResponse,
    SubjectFirstMarkResponse,
    TopperResponse,
)
from fastapi import Depends, FastAPI, Form, HTTPException, Query, status
from models import HSC, SSLC, Group, HSCStudentData, JsonDump, SSLCStudentData
from sqlalchemy import or_
from sqlmodel import Session, SQLModel, desc, func, select, text

from database import engine, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="School Result Organizing Microservice", lifespan=lifespan)


# --- AUTH ENDPOINT ---
@app.get("/auth/login")
def login():

    return {"message": "Login successful stub"}


@app.post("/auth/register")
# register user and generate otp
@app.get("/auth/verify_otp")
# verify the otp and send the JWT


# --- STUDENT DATA SUBMISSION (FORM POSTS) ---
@app.post("/submit/sslc", response_model=StudentSubmitResponse)
def submit_sslc(
    form_data: SSLCStudentForm = Depends(SSLCStudentForm.as_form),
    session: Session = Depends(get_session),
):
    """Accept SSLC student registration details from the student details form.
    Validates input via SSLCStudentForm DTO + saves to sslc_student_data table.
    """
    student = SSLCStudentData(
        reg_no=form_data.reg_no,
        name=form_data.name.upper(),
        class_=form_data.sec,
        dob=form_data.dob,
    )

    session.add(student)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to save SSLC student data (possible duplicate reg_no?): {str(e)}",
        )

    return StudentSubmitResponse(
        message="success",
        name=form_data.name.upper(),
        reg_no=form_data.reg_no,
    )


@app.post("/submit/hsc", response_model=StudentSubmitResponse)
def submit_hsc(
    form_data: HSCStudentForm = Depends(HSCStudentForm.as_form),
    session: Session = Depends(get_session),
):
    """Accept HSC student registration details from the student details form.
    Validates input via HSCStudentForm DTO + saves to hsc_student_data table.
    """
    student = HSCStudentData(
        reg_no=form_data.reg_no,
        name=form_data.name.upper(),
        class_=form_data.sec,
        dob=form_data.dob,
        group_code=form_data.grp,
    )

    session.add(student)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to save HSC student data (possible duplicate reg_no?): {str(e)}",
        )

    return StudentSubmitResponse(
        message="success",
        name=form_data.name.upper(),
        reg_no=form_data.reg_no,
    )


def build_exam_result_summary(session: Session, model) -> ExamResultSummaryDTO:
    appeared = session.scalar(select(func.count()).select_from(model)) or 0
    passed = (
        session.scalar(
            select(func.count())
            .select_from(model)
            .where(func.upper(model.result) == "PASS")
        )
        or 0
    )
    failed = (
        session.scalar(
            select(func.count())
            .select_from(model)
            .where(func.upper(model.result) == "FAIL")
        )
        or 0
    )
    pass_percentage = round((passed / appeared) * 100, 2) if appeared else 0.0

    return ExamResultSummaryDTO(
        appeared=appeared,
        passed=passed,
        failed=failed,
        pass_percentage=pass_percentage,
    )


@app.get("/results", response_model=ResultsSummaryDTO)
def get_exam_results_summary(session: Session = Depends(get_session)):
    """Return appeared, passed, failed counts and pass percentage for HSC and SSLC."""
    return ResultsSummaryDTO(
        hsc=build_exam_result_summary(session, HSC),
        sslc=build_exam_result_summary(session, SSLC),
    )


# --- STUDENT DATA GET (all rows) ---
@app.get("/sslc/student-data", response_model=List[SSLCStudentDataResponse])
def get_all_sslc_student_data(session: Session = Depends(get_session)):
    """Return all rows from sslc_student_data table (registration / student details form data)."""
    results = session.exec(select(SSLCStudentData)).all()
    return [
        SSLCStudentDataResponse(
            reg_no=row.reg_no,
            name=row.name,
            class_=row.class_,
            dob=row.dob.strftime("%d-%m-%Y"),
        )
        for row in results
    ]


@app.get("/hsc/student-data", response_model=List[HSCStudentDataResponse])
def get_all_hsc_student_data(session: Session = Depends(get_session)):
    """Return all rows from hsc_student_data table (registration / student details form data)."""
    results = session.exec(select(HSCStudentData)).all()
    return [
        HSCStudentDataResponse(
            reg_no=row.reg_no,
            name=row.name,
            class_=row.class_,
            dob=row.dob.strftime("%d-%m-%Y"),
            group_code=row.group_code,
        )
        for row in results
    ]


def section_sort_key(sec: str) -> tuple:
    """Custom sort so that 'A1' comes before 'A', 'G2' before 'G', etc.
    Plain letter sections (no trailing number) sort after their numbered variants.
    """
    sec = (sec or "").strip()
    i = len(sec) - 1
    while i >= 0 and sec[i].isdigit():
        i -= 1
    letter_part = sec[: i + 1].upper()
    num_part = sec[i + 1 :]
    num = int(num_part) if num_part else 9999
    return (letter_part, num)


def row_to_sslc_topper_response(row) -> SSLCTopperResponse:
    return SSLCTopperResponse(
        rank=row.rank,
        reg_no=row.reg_no,
        class_=row.class_name,
        name=row.name,
        tamil=row.tamil,
        english=row.english,
        maths=row.maths,
        science=row.science,
        social=row.social,
        total=row.total if row.total is not None else 0,
    )


def row_to_sslc_failure_response(row) -> SSLCFailureResponse:
    return SSLCFailureResponse(
        reg_no=row.reg_no,
        class_=row.class_name,
        name=row.name,
        tamil=row.tamil,
        english=row.english,
        maths=row.maths,
        science=row.science,
        social=row.social,
        total=row.total if row.total is not None else 0,
    )


# --- SSLC ENDPOINTS ---
@app.get("/sslc/classwise", response_model=List[SSLCTopperResponse])
def get_sslc_classwise(class_name: str, session: Session = Depends(get_session)):
    """Get SSLC students filtered by class, ranked by total marks descending."""
    statement = (
        select(
            func.dense_rank().over(order_by=desc(SSLC.total)).label("rank"),
            SSLC.reg_no,
            SSLC.class_.label("class_name"),
            SSLC.name,
            SSLC.tamil,
            SSLC.english,
            SSLC.maths,
            SSLC.science,
            SSLC.social,
            SSLC.total,
        )
        .where(SSLC.class_ == class_name)
        .order_by(desc(SSLC.total))
    )

    results = session.exec(statement).all()

    return [row_to_sslc_topper_response(row) for row in results]


@app.get("/sslc/sections", response_model=List[SectionDTO])
def get_sslc_sections(session: Session = Depends(get_session)):
    """Return all SSLC class sections (no groups — SSLC has no streams)."""
    statement = select(SSLC.class_).distinct()
    rows = session.exec(statement).all()
    classes = sorted({row for row in rows if row}, key=section_sort_key)
    return [SectionDTO(sec=sec, grp=[]) for sec in classes]


@app.get("/sslc/failures", response_model=List[SSLCFailureResponse])
def get_sslc_failures(session: Session = Depends(get_session)):
    """Return all SSLC students with result FAIL, ordered by total marks descending."""
    statement = (
        select(
            SSLC.reg_no,
            SSLC.class_.label("class_name"),
            SSLC.name,
            SSLC.tamil,
            SSLC.english,
            SSLC.maths,
            SSLC.science,
            SSLC.social,
            SSLC.total,
        )
        .where(func.upper(SSLC.result) == "FAIL")
        .order_by(desc(SSLC.total))
    )

    results = session.exec(statement).all()

    return [row_to_sslc_failure_response(row) for row in results]


@app.get("/sslc/toppers", response_model=List[SSLCTopperResponse])
def get_sslc_toppers(limit: int = 10, session: Session = Depends(get_session)):
    """Get overall top SSLC students based on total marks with dense ranking."""
    statement = select(SSLC).order_by(SSLC.total.desc()).limit(limit)
    results = session.exec(statement).all()

    if not results:
        return []

    toppers = []
    current_rank = 1
    previous_total = None

    for student in results:
        student_total = student.total if student.total is not None else 0

        if previous_total is not None and student_total < previous_total:
            current_rank += 1

        toppers.append(
            SSLCTopperResponse(
                rank=current_rank,
                reg_no=student.reg_no,
                class_=student.class_,
                name=student.name,
                tamil=student.tamil,
                english=student.english,
                maths=student.maths,
                science=student.science,
                social=student.social,
                total=student_total,
            )
        )
        previous_total = student_total

    return toppers


@app.get("/sslc/subject-first-marks", response_model=List[SubjectFirstMarkResponse])
def get_sslc_subject_first_marks(session: Session = Depends(get_session)):
    """Get highest marks per subject and count of students who achieved them (SSLC)."""
    query = text("""
        WITH unpivoted_subjects AS (
            SELECT 'TAMIL' AS subject_name, tamil AS mark FROM sslc WHERE tamil IS NOT NULL
            UNION ALL
            SELECT 'ENGLISH' AS subject_name, english AS mark FROM sslc WHERE english IS NOT NULL
            UNION ALL
            SELECT 'MATHS' AS subject_name, maths AS mark FROM sslc WHERE maths IS NOT NULL
            UNION ALL
            SELECT 'SCIENCE' AS subject_name, science AS mark FROM sslc WHERE science IS NOT NULL
            UNION ALL
            SELECT 'SOCIAL' AS subject_name, social AS mark FROM sslc WHERE social IS NOT NULL
        ),
        max_marks_per_subject AS (
            SELECT
                subject_name,
                MAX(mark) as max_mark
            FROM unpivoted_subjects
            GROUP BY subject_name
        )
        SELECT
            u.subject_name AS name,
            u.mark AS mark,
            COUNT(*) AS count
        FROM unpivoted_subjects u
        JOIN max_marks_per_subject m
          ON u.subject_name = m.subject_name AND u.mark = m.max_mark
        GROUP BY u.subject_name, u.mark
        ORDER BY CASE u.subject_name
            WHEN 'TAMIL' THEN 1
            WHEN 'ENGLISH' THEN 2
            WHEN 'MATHS' THEN 3
            WHEN 'SCIENCE' THEN 4
            WHEN 'SOCIAL' THEN 5
            ELSE 6
        END;
    """)

    result = session.execute(query).mappings().all()

    subject_order = {"TAMIL": 0, "ENGLISH": 1, "MATHS": 2, "SCIENCE": 3, "SOCIAL": 4}
    return sorted(
        [
            SubjectFirstMarkResponse(
                name=row["name"], mark=row["mark"], count=row["count"]
            )
            for row in result
        ],
        key=lambda item: subject_order.get(item.name.upper(), 99),
    )


@app.get("/sslc/subject/toppers", response_model=List[SSLCTopperResponse])
def get_sslc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    """Get top students for a specific SSLC subject."""
    valid_subjects = {"tamil", "english", "maths", "science", "social"}
    subject_lower = subject.lower()

    if subject_lower not in valid_subjects:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid subject '{subject}'. Valid subjects: {', '.join(sorted(valid_subjects))}",
        )

    subject_col = getattr(SSLC, subject_lower)

    statement = (
        select(
            func.dense_rank().over(order_by=desc(subject_col)).label("rank"),
            SSLC.reg_no,
            SSLC.class_.label("class_name"),
            SSLC.name,
            SSLC.tamil,
            SSLC.english,
            SSLC.maths,
            SSLC.science,
            SSLC.social,
            SSLC.total,
        )
        .where(subject_col.isnot(None))
        .order_by(desc(subject_col))
        .limit(limit)
    )

    results = session.exec(statement).all()

    return [row_to_sslc_topper_response(row) for row in results]


# --- HSC sections/groups helpers (used by /hsc/sections) ---
def lookup_group_by_code(session: Session, code: Optional[str]) -> Optional[Group]:
    if not code:
        return None
    return session.exec(
        select(Group).where(func.lower(Group.code) == code.strip().lower())
    ).first()


def hsc_group_join():
    return or_(
        HSC.group_id == Group.group_id,
        func.lower(HSC.group_code) == func.lower(Group.code),
    )


def row_to_student_groupwise_dto(row) -> StudentGroupwiseDTO:
    return StudentGroupwiseDTO(
        rank=row.rank,
        reg_no=row.reg_no,
        class_=row.class_name,
        group=row.group,
        name=row.name,
        lang_name=row.lang_name,
        lang=row.lang or 0,
        eng=row.eng or 0,
        sub1=row.sub1 or 0,
        sub2=row.sub2 or 0,
        sub3=row.sub3 or 0,
        sub4=row.sub4,
        total=row.total,
        cutoff=row.cutoff,
    )


def row_to_hsc_failure_response(row) -> HSCFailureResponse:
    return HSCFailureResponse(
        reg_no=row.reg_no,
        class_=row.class_name,
        group=row.group,
        name=row.name,
        lang_name=row.lang_name,
        lang=row.lang or 0,
        eng=row.eng or 0,
        sub1=row.sub1 or 0,
        sub2=row.sub2 or 0,
        sub3=row.sub3 or 0,
        sub4=row.sub4,
        total=row.total if row.total is not None else 0,
        cutoff=row.cutoff,
    )


def hsc_to_topper(rank: int, student: HSC) -> TopperResponse:
    return TopperResponse(
        rank=rank,
        reg_no=student.reg_no,
        class_=student.class_,
        group=student.group_code,
        name=student.name,
        lang_name=student.lang_name,
        lang=student.lang or 0,
        eng=student.eng or 0,
        sub1=student.mark_1 or 0,
        sub2=student.mark_2 or 0,
        sub3=student.mark_3 or 0,
        sub4=student.mark_4,
        total=student.total if student.total is not None else 0,
        cutoff=student.cut_off,
    )


HSC_SUBJECT_NAME_MAP = {
    "CHEM": "CHEMISTRY",
    "PHY": "PHYSICS",
    "MATHS": "MATHEMATICS",
    "COMP": "COMPUTER SCIENCE",
    "CSC": "COMPUTER SCIENCE",
    "BIO": "BIOLOGY",
    "ACC": "ACCOUNTANCY",
    "ECO": "ECONOMICS",
    "COM": "COMMERCE",
    "CA": "COMPUTER APPLICATION",
    "BM": "BUSINESS MATHEMATICS",
    "BME (THY)": "BASIC MECHANICAL ENGINEERING (THEORY)",
    "BME (PRT)": "BASIC MECHANICAL ENGINEERING (PRACTICAL)",
    "ES": "EMPLOYABILITY SKILLS",
}


def subject_label(subject: Optional[str]) -> str:
    """Format a subject name loaded from the groups table for API responses."""
    if not subject:
        return ""
    return subject.strip().upper()


def hsc_subject_display_name(subject: Optional[str]) -> str:
    """Map HSC subject short codes to full display names."""
    if not subject:
        return ""
    key = subject.strip().upper()
    return HSC_SUBJECT_NAME_MAP.get(key, key)


def group_dto_from_db_row(row) -> GroupDTO:
    """Build a GroupDTO from a groups (+ section) query row."""
    code = (row.code or "").strip().lower()
    return GroupDTO(
        name=row.group_name or code.upper(),
        code=code,
        sub1=subject_label(row.subject1),
        sub2=subject_label(row.subject2),
        sub3=subject_label(row.subject3),
        sub4=subject_label(row.subject4) if row.subject4 else None,
    )


def get_groups_by_code(session: Session) -> dict[str, Group]:
    """Load all groups from the database keyed by lowercase code."""
    return {
        group.code.lower(): group
        for group in session.exec(select(Group).order_by(Group.group_id)).all()
    }


def parse_result_value(raw: Optional[str], reg_no: Optional[str] = None) -> str:
    """Normalize and validate a PASS/FAIL result from CSV import."""
    value = (raw or "").strip().upper()
    if value not in {"PASS", "FAIL"}:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid result '{raw}' for reg_no {reg_no}. Expected PASS or FAIL."
            ),
        )
    return value


HSC_CLASS_DETAILS_KEY = "hsc-class-details"


@app.get("/hsc-class-details/submit")
def get_hsc_class_details(session: Session = Depends(get_session)):
    record = session.get(JsonDump, HSC_CLASS_DETAILS_KEY)
    if record is None:
        return []
    return record.data


@app.post("/hsc-class-details/submit")
def submit_hsc_class_details(
    payload: Any,
    session: Session = Depends(get_session),
):
    record = session.get(JsonDump, HSC_CLASS_DETAILS_KEY)
    if record is None:
        record = JsonDump(key=HSC_CLASS_DETAILS_KEY, data=payload)
    else:
        record.data = payload
    session.add(record)
    session.commit()
    session.refresh(record)
    return record.data


# --- HSC ENDPOINTS ---
@app.get("/hsc/groupwise", response_model=GroupwiseResponseDTO)
def get_hsc_groupwise(
    group_name: str = "BIOMAT", session: Session = Depends(get_session)
):
    statement = (
        select(
            func.dense_rank().over(order_by=desc(HSC.total)).label("rank"),
            HSC.reg_no,
            HSC.class_.label("class_name"),
            HSC.group_code.label("group"),
            HSC.name,
            HSC.lang_name,
            HSC.lang,
            HSC.eng,
            HSC.mark_1.label("sub1"),
            HSC.mark_2.label("sub2"),
            HSC.mark_3.label("sub3"),
            HSC.mark_4.label("sub4"),
            HSC.total,
            HSC.cut_off.label("cutoff"),
        )
        .where(func.lower(HSC.group_code) == group_name.lower())
        .order_by(desc(HSC.total))
    )

    results = session.exec(statement).all()

    students = [row_to_student_groupwise_dto(row) for row in results]

    return GroupwiseResponseDTO(datas=students)


@app.get("/hsc/classwise", response_model=List[StudentGroupwiseDTO])
def get_hsc_classwise(class_name: str, session: Session = Depends(get_session)):
    """Get HSC students filtered by class, ranked by total marks descending."""
    statement = (
        select(
            func.dense_rank().over(order_by=desc(HSC.total)).label("rank"),
            HSC.reg_no,
            HSC.class_.label("class_name"),
            HSC.group_code.label("group"),
            HSC.name,
            HSC.lang_name,
            HSC.lang,
            HSC.eng,
            HSC.mark_1.label("sub1"),
            HSC.mark_2.label("sub2"),
            HSC.mark_3.label("sub3"),
            HSC.mark_4.label("sub4"),
            HSC.total,
            HSC.cut_off.label("cutoff"),
        )
        .where(HSC.class_ == class_name)
        .order_by(desc(HSC.total))
    )

    results = session.exec(statement).all()

    return [row_to_student_groupwise_dto(row) for row in results]


@app.get("/hsc/failures", response_model=List[HSCFailureResponse])
def get_hsc_failures(session: Session = Depends(get_session)):
    """Return all HSC students with result FAIL, ordered by total marks descending."""
    statement = (
        select(
            HSC.reg_no,
            HSC.class_.label("class_name"),
            HSC.group_code.label("group"),
            HSC.name,
            HSC.lang_name,
            HSC.lang,
            HSC.eng,
            HSC.mark_1.label("sub1"),
            HSC.mark_2.label("sub2"),
            HSC.mark_3.label("sub3"),
            HSC.mark_4.label("sub4"),
            HSC.total,
            HSC.cut_off.label("cutoff"),
        )
        .where(func.upper(HSC.result) == "FAIL")
        .order_by(desc(HSC.total))
    )

    results = session.exec(statement).all()

    return [row_to_hsc_failure_response(row) for row in results]


@app.get("/hsc/sections", response_model=List[SectionDTO])
def get_hsc_sections(session: Session = Depends(get_session)):
    """
    Return all available class sections (sec) together with the groups/streams (grp)
    that exist for students in that section.

    Data is derived from HSC rows joined to the groups table (distinct class + group).
    Uses display names and short subject codes for frontend use.
    """
    statement = (
        select(
            HSC.class_.label("sec"),
            Group.code,
            Group.name.label("group_name"),
            Group.subject1,
            Group.subject2,
            Group.subject3,
            Group.subject4,
        )
        .join(Group, hsc_group_join())
        .distinct()
        .order_by(HSC.class_, Group.code)
    )

    rows = session.exec(statement).all()

    from collections import defaultdict

    sec_to_groups = defaultdict(list)
    seen = set()

    for row in rows:
        sec = row.sec
        code = (row.code or "").strip().lower()
        if not sec or not code:
            continue

        key = (sec, code)
        if key in seen:
            continue
        seen.add(key)

        g = group_dto_from_db_row(row)
        sec_to_groups[sec].append(g)

    # Build final ordered list
    result: List[SectionDTO] = []
    for sec in sorted(sec_to_groups.keys(), key=section_sort_key):
        # Sort groups inside each section by code for stable order
        grps = sorted(sec_to_groups[sec], key=lambda g: g.code)
        result.append(SectionDTO(sec=sec, grp=grps))

    return result


@app.get("/hsc/toppers")
def get_hsc_toppers(limit: int = 10, session: Session = Depends(get_session)):
    # 1. Fetch records ordered by total marks descending
    statement = select(HSC).order_by(HSC.total.desc()).limit(limit)
    results = session.exec(statement).all()

    if not results:
        return []

    toppers = []

    # Track ranking states
    current_rank = 1
    previous_total = None

    # 2. Assign ranks dynamically based on total score ties
    for student in results:
        student_total = student.total if student.total is not None else 0

        # If score dropped, increment rank by 1 (Dense Ranking / 1-2-2-3)
        if previous_total is not None and student_total < previous_total:
            current_rank += 1

        toppers.append(hsc_to_topper(current_rank, student))
        # Update previous total for the next iteration
        previous_total = student_total

    return toppers


@app.get("/hsc/subject-first-marks", response_model=List[SubjectFirstMarkResponse])
def get_subject_first_marks(session: Session = Depends(get_session)):
    # Raw SQL query to unpivot the subject columns, find max marks, and count achievers
    query = text("""
        WITH unpivoted_subjects AS (
            SELECT g.subject1 AS subject_name, h.mark_1 AS mark
            FROM hsc h
            JOIN groups g ON (
                h.group_id = g.group_id
                OR (h.group_id IS NULL AND LOWER(h.group_code) = LOWER(g.code))
            )
            WHERE g.subject1 IS NOT NULL AND h.mark_1 IS NOT NULL
            UNION ALL
            SELECT g.subject2, h.mark_2
            FROM hsc h
            JOIN groups g ON (
                h.group_id = g.group_id
                OR (h.group_id IS NULL AND LOWER(h.group_code) = LOWER(g.code))
            )
            WHERE g.subject2 IS NOT NULL AND h.mark_2 IS NOT NULL
            UNION ALL
            SELECT g.subject3, h.mark_3
            FROM hsc h
            JOIN groups g ON (
                h.group_id = g.group_id
                OR (h.group_id IS NULL AND LOWER(h.group_code) = LOWER(g.code))
            )
            WHERE g.subject3 IS NOT NULL AND h.mark_3 IS NOT NULL
            UNION ALL
            SELECT g.subject4, h.mark_4
            FROM hsc h
            JOIN groups g ON (
                h.group_id = g.group_id
                OR (h.group_id IS NULL AND LOWER(h.group_code) = LOWER(g.code))
            )
            WHERE g.subject4 IS NOT NULL AND h.mark_4 IS NOT NULL
        ),
        max_marks_per_subject AS (
            SELECT
                subject_name,
                MAX(mark) as max_mark
            FROM unpivoted_subjects
            GROUP BY subject_name
        )
        SELECT
            u.subject_name AS name,
            u.mark AS mark,
            COUNT(*) AS count
        FROM unpivoted_subjects u
        JOIN max_marks_per_subject m
          ON u.subject_name = m.subject_name AND u.mark = m.max_mark
        GROUP BY u.subject_name, u.mark
        ORDER BY count DESC;
    """)

    # Execute query
    result = session.execute(query).mappings().all()

    return [
        SubjectFirstMarkResponse(
            name=hsc_subject_display_name(row["name"]),
            mark=row["mark"],
            count=row["count"],
        )
        for row in result
    ]


@app.get("/hsc/subject/toppers", response_model=List[TopperResponse])
def get_hsc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    """Get top students for a specific HSC subject."""
    # Map API subject names to model columns (sm* aliases kept for compatibility)
    subject_map = {
        "lang": HSC.lang,
        "eng": HSC.eng,
        "sm1": HSC.mark_1,
        "sm2": HSC.mark_2,
        "sm3": HSC.mark_3,
        "sm4": HSC.mark_4,
        "mark_1": HSC.mark_1,
        "mark_2": HSC.mark_2,
        "mark_3": HSC.mark_3,
        "mark_4": HSC.mark_4,
    }
    mark_attr_map = {
        "lang": "lang",
        "eng": "eng",
        "sm1": "mark_1",
        "sm2": "mark_2",
        "sm3": "mark_3",
        "sm4": "mark_4",
        "mark_1": "mark_1",
        "mark_2": "mark_2",
        "mark_3": "mark_3",
        "mark_4": "mark_4",
    }
    subject_lower = subject.lower()

    if subject_lower not in subject_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid subject '{subject}'. Valid subjects: {', '.join(sorted(subject_map.keys()))}",
        )

    subject_col = subject_map[subject_lower]

    statement = (
        select(HSC)
        .where(subject_col.isnot(None))
        .order_by(desc(subject_col))
        .limit(limit)
    )

    results = session.exec(statement).all()

    toppers = []
    current_rank = 1
    previous_mark = None

    for student in results:
        student_mark = getattr(student, mark_attr_map[subject_lower]) or 0

        if previous_mark is not None and student_mark < previous_mark:
            current_rank += 1

        toppers.append(hsc_to_topper(current_rank, student))
        previous_mark = student_mark

    return toppers


# --- IMPORT HSC DATA ---
@app.get("/import_hsc")
def import_hsc_csv(
    file_path: str = "mock_data/hsc.csv",
    class_name: str = "XII-A1",
    group_name: str = "csc",
    db: Session = Depends(get_session),
):
    """
    GET endpoint to read the CSV file, parse the data,
    and insert rows into PostgreSQL.
    cut_off is computed automatically by the database using GENERATED ALWAYS AS.
    """
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            # Normalize column headers to handle any accidental leading/trailing spaces
            reader.fieldnames = (
                [field.strip().upper() for field in reader.fieldnames]
                if reader.fieldnames
                else []
            )

            group = lookup_group_by_code(db, group_name)
            normalized_group_code = group_name.strip().lower()
            records_to_insert = []

            for row in reader:
                # Parse numeric marks safely
                physics = int(row["PHYSICS"])
                chemistry = int(row["CHEMISTRY"])
                comp_or_third = int(row["COMP"])
                maths = int(row["MATHS"])

                hsc_record = HSC(
                    reg_no=int(row["REGNO"]),
                    class_=class_name,
                    name=row["NAME"].strip(),
                    group_id=group.group_id if group else None,
                    group_code=normalized_group_code,
                    lang=int(row["TAMIL"]),
                    eng=int(row["ENGLISH"]),
                    mark_1=physics,
                    mark_2=chemistry,
                    mark_3=comp_or_third,
                    mark_4=maths,
                    result=parse_result_value(row.get("RESULT"), row.get("REGNO")),
                    # cut_off is DB-generated (do not set it here)
                )
                records_to_insert.append(hsc_record)

            if not records_to_insert:
                raise HTTPException(
                    status_code=400, detail="The provided CSV file contains no records."
                )

            # Bulk add and commit to PostgreSQL
            db.add_all(records_to_insert)
            db.commit()

            return {
                "status": "success",
                "inserted_records": len(records_to_insert),
                "message": f"Successfully loaded {len(records_to_insert)} student records into the hsc table.",
            }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"The CSV file could not be found at the path: '{file_path}'",
        )
    except KeyError as e:
        raise HTTPException(
            status_code=422, detail=f"Missing expected column in CSV file: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while writing to the database: {str(e)}",
        )


@app.get("/import_sslc")
def import_sslc_csv(
    file_path: str = "mock_data/sslc.csv",
    class_char: str = Query(
        ...,
        min_length=1,
        max_length=1,
        description="Single character class label, e.g., 'A'",
    ),
    db: Session = Depends(get_session),
):
    """
    GET endpoint to parse the SSLC CSV document, split full names into
    first_name and last_name components, and execute a bulk database insert.
    """
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            # Standardize column headers to avoid trailing or leading whitespace mismatches
            reader.fieldnames = (
                [field.strip().upper() for field in reader.fieldnames]
                if reader.fieldnames
                else []
            )

            records_to_insert = []

            for row in reader:
                full_name = row["NAME"].strip()
                sslc_record = SSLC(
                    reg_no=int(row["REGNO"]),
                    class_=class_char,
                    name=full_name,
                    tamil=int(row["TAMIL"]) if row.get("TAMIL") else None,
                    english=int(row["ENGLISH"]) if row.get("ENGLISH") else None,
                    maths=int(row["MATHS"]) if row.get("MATHS") else None,
                    science=int(row["SCIENCE"]) if row.get("SCIENCE") else None,
                    social=int(row["SOCIAL"]) if row.get("SOCIAL") else None,
                    result=parse_result_value(row.get("RESULT"), row.get("REGNO")),
                )
                records_to_insert.append(sslc_record)

            if not records_to_insert:
                raise HTTPException(
                    status_code=400,
                    detail="The provided CSV file contains no valid rows.",
                )

            # Perform a bulk save operation and commit to the Postgres database
            db.add_all(records_to_insert)
            db.commit()

            return {
                "status": "success",
                "inserted_records": len(records_to_insert),
                "message": f"Successfully parsed and loaded {len(records_to_insert)} records into the sslc table.",
            }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"The requested CSV file could not be found at the path: '{file_path}'",
        )
    except KeyError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Missing an expected column header in the CSV file: {str(e)}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during database injection: {str(e)}",
        )


@app.get("/import_hsc_mock")
def import_mock_hsc_csv(
    file_path: str = "mock_data/tn_hsc_exam_data.csv",
    db: Session = Depends(get_session),
):
    """
    GET endpoint to read the HSC mock CSV and insert rows into PostgreSQL.
    CSV columns: reg_no, class, name, group_code, lang_name, lang, eng,
    mark_1, mark_2, mark_3, mark_4, result.
    total and cut_off are computed by the database (GENERATED ALWAYS AS).
    """
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            # Normalize column headers to handle any accidental spaces and lowercase them
            reader.fieldnames = (
                [field.strip().lower() for field in reader.fieldnames]
                if reader.fieldnames
                else []
            )

            required_columns = {
                "reg_no",
                "class",
                "name",
                "group_code",
                "lang_name",
                "lang",
                "eng",
                "mark_1",
                "mark_2",
                "mark_3",
                "mark_4",
                "result",
            }
            missing_columns = required_columns - set(reader.fieldnames or [])
            if missing_columns:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "CSV is missing required columns: "
                        f"{', '.join(sorted(missing_columns))}"
                    ),
                )

            groups_by_code = get_groups_by_code(db)
            records_to_insert = []
            pass_count = 0
            fail_count = 0

            for row in reader:
                group_code = (row.get("group_code") or "").strip().lower()
                if not group_code:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Missing group_code for reg_no {row.get('reg_no')}",
                    )

                group = groups_by_code.get(group_code)
                if group is None:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Unknown group_code '{group_code}' for reg_no {row.get('reg_no')}",
                    )

                def get_optional_int(key: str) -> Optional[int]:
                    val = row.get(key)
                    if val is None:
                        return None
                    val = val.strip()
                    return int(val) if val != "" else None

                result = parse_result_value(row.get("result"), row.get("reg_no"))
                if result == "PASS":
                    pass_count += 1
                else:
                    fail_count += 1

                hsc_record = HSC(
                    reg_no=int(row["reg_no"]),
                    class_=row["class"].strip(),
                    name=row["name"].strip(),
                    group_id=group.group_id,
                    group_code=group_code,
                    lang_name=row["lang_name"].strip(),
                    lang=int(row["lang"]),
                    eng=int(row["eng"]),
                    mark_1=get_optional_int("mark_1"),
                    mark_2=get_optional_int("mark_2"),
                    mark_3=get_optional_int("mark_3"),
                    mark_4=get_optional_int("mark_4"),
                    result=result,
                )
                records_to_insert.append(hsc_record)

            if not records_to_insert:
                raise HTTPException(
                    status_code=400,
                    detail="The provided CSV file contains no records.",
                )

            # Bulk add and commit to PostgreSQL database
            db.add_all(records_to_insert)
            db.commit()

            return {
                "status": "success",
                "inserted_records": len(records_to_insert),
                "passed": pass_count,
                "failed": fail_count,
                "message": (
                    f"Successfully loaded {len(records_to_insert)} student records "
                    f"into the hsc table ({pass_count} passed, {fail_count} failed)."
                ),
            }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"The CSV file could not be found at the path: '{file_path}'",
        )
    except KeyError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Missing expected column in CSV file: {str(e)}",
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while writing to the database: {str(e)}",
        )


@app.get("/import_sslc_mock")
def import_mock_sslc_csv(
    file_path: str = "mock_data/tn_sslc_exam_data.csv",
    db: Session = Depends(get_session),
):
    """
    GET endpoint to read the SSLC mock CSV and insert rows into PostgreSQL.
    CSV columns: reg_no, class, name, tamil, english, maths, science, social, result.
    total is computed by the database (GENERATED ALWAYS AS).
    """
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            reader.fieldnames = (
                [
                    "reg_no"
                    if field.strip().lower() == "regno"
                    else field.strip().lower()
                    for field in reader.fieldnames
                ]
                if reader.fieldnames
                else []
            )

            required_columns = {
                "reg_no",
                "class",
                "name",
                "tamil",
                "english",
                "maths",
                "science",
                "social",
                "result",
            }
            missing_columns = required_columns - set(reader.fieldnames or [])
            if missing_columns:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "CSV is missing required columns: "
                        f"{', '.join(sorted(missing_columns))}"
                    ),
                )

            records_to_insert = []
            pass_count = 0
            fail_count = 0

            for row in reader:

                def get_optional_int(key: str) -> Optional[int]:
                    val = row.get(key)
                    if val is None:
                        return None
                    val = val.strip()
                    return int(val) if val != "" else None

                result = parse_result_value(row.get("result"), row.get("reg_no"))
                if result == "PASS":
                    pass_count += 1
                else:
                    fail_count += 1

                sslc_record = SSLC(
                    reg_no=int(row["reg_no"]),
                    class_=row["class"].strip(),
                    name=row["name"].strip(),
                    tamil=get_optional_int("tamil"),
                    english=get_optional_int("english"),
                    maths=get_optional_int("maths"),
                    science=get_optional_int("science"),
                    social=get_optional_int("social"),
                    result=result,
                )
                records_to_insert.append(sslc_record)

            if not records_to_insert:
                raise HTTPException(
                    status_code=400,
                    detail="The provided CSV file contains no records.",
                )

            db.add_all(records_to_insert)
            db.commit()

            return {
                "status": "success",
                "inserted_records": len(records_to_insert),
                "passed": pass_count,
                "failed": fail_count,
                "message": (
                    f"Successfully loaded {len(records_to_insert)} student records "
                    f"into the sslc table ({pass_count} passed, {fail_count} failed)."
                ),
            }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"The CSV file could not be found at the path: '{file_path}'",
        )
    except KeyError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Missing expected column in CSV file: {str(e)}",
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while writing to the database: {str(e)}",
        )
