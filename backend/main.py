import csv
from contextlib import asynccontextmanager
from datetime import date
from typing import List, Optional

from DTOs import (
    GroupDTO,
    GroupwiseResponseDTO,
    HSCStudentDataResponse,
    HSCStudentForm,
    SectionDTO,
    SSLCClasswiseResponseDTO,
    SSLCStudentDataResponse,
    SSLCStudentForm,
    SSLCTopperResponse,
    StudentGroupwiseDTO,
    StudentSubmitResponse,
    SubjectFirstMarkResponse,
    TopperResponse,
)
from fastapi import Depends, FastAPI, Form, HTTPException, Query, status
from models import HSC, SSLC, HSCStudentData, SSLCStudentData
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
            dob=row.dob,
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
            dob=row.dob,
            group_code=row.group_code,
        )
        for row in results
    ]


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

    return [
        SSLCTopperResponse(
            rank=row.rank,
            reg_no=row.reg_no,
            class_=row.class_name,
            name=row.name,
            tamil=row.tamil,
            english=row.english,
            maths=row.maths,
            science=row.science,
            social=row.social,
            total=row.total,
        )
        for row in results
    ]


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
        ORDER BY count DESC;
    """)

    result = session.execute(query).mappings().all()

    return [
        SubjectFirstMarkResponse(name=row["name"], mark=row["mark"], count=row["count"])
        for row in result
    ]


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

    return [
        SSLCTopperResponse(
            rank=row.rank,
            reg_no=row.reg_no,
            class_=row.class_name,
            name=row.name,
            tamil=row.tamil,
            english=row.english,
            maths=row.maths,
            science=row.science,
            social=row.social,
            total=row.total,
        )
        for row in results
    ]


# --- HSC sections/groups helpers (used by /hsc/sections) ---
GROUP_DISPLAY_NAMES: dict[str, str] = {
    "csc": "COMPUTER SCIENCE + MATHS",
    "biomat": "BIOLOGY + MATHS",
    "biocs": "BIOLOGY + COMPUTER SCIENCE",
    "artsbm": "ARTS + BUSINESS MATHEMATICS",
    "artsca": "ARTS + COMPUTER APPLICATIONS",
    "bme": "BASIC MECHANICAL ENGINEERING (BME)",
}


def abbreviate_subject(subject: Optional[str]) -> str:
    """Convert full subject name from DB (e.g. 'Computer Science') to short code used by frontend (e.g. 'COMP')."""
    if not subject:
        return ""
    s = subject.strip().lower()
    abbrev_map = {
        "physics": "PHY",
        "chemistry": "CHEM",
        "computer science": "COMP",
        "mathematics": "MATHS",
        "biology": "BIO",
        "economics": "ECO",
        "commerce": "COM",
        "accountancy": "ACC",
        "business mathematics": "BM",
        "computer applications": "CA",
        "bme (theory)": "BME(THY)",
        "bme (practical)": "BME(PRT)",
        "employability skills": "ES",
    }
    if s in abbrev_map:
        return abbrev_map[s]
    # Fallback for unknown/new subjects
    words = [w for w in s.split() if w]
    if len(words) >= 2:
        return "".join(w[0].upper() for w in words)[:6]
    return s.upper()[:6] or "SUB"


def section_sort_key(sec: str) -> tuple:
    """Custom sort so that 'A1' comes before 'A', 'G2' before 'G', etc.
    Plain letter sections (no trailing number) sort after their numbered variants.
    """
    sec = (sec or "").strip()
    # Walk backwards to separate trailing digits
    i = len(sec) - 1
    while i >= 0 and sec[i].isdigit():
        i -= 1
    letter_part = sec[: i + 1].upper()
    num_part = sec[i + 1 :]
    num = int(num_part) if num_part else 9999
    return (letter_part, num)


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
            HSC.group_name.label("group"),
            HSC.name,
            HSC.lang_name,
            HSC.lang,
            HSC.eng,
            HSC.sm1.label("sub1"),
            HSC.sm2.label("sub2"),
            HSC.sm3.label("sub3"),
            HSC.sm4.label("sub4"),
            HSC.total,
            HSC.cut_off.label("cutoff"),
        )
        .where(HSC.group_name == group_name)
        .order_by(desc(HSC.total))
    )

    results = session.exec(statement).all()

    students = [
        StudentGroupwiseDTO(
            rank=row.rank,
            reg_no=row.reg_no,
            class_=row.class_name,
            group=row.group,
            name=row.name,
            lang_name=row.lang_name,
            lang=row.lang,
            eng=row.eng,
            sub1=row.sub1,
            sub2=row.sub2,
            sub3=row.sub3,
            sub4=row.sub4,
            total=row.total,
            cutoff=row.cutoff,
        )
        for row in results
    ]

    return GroupwiseResponseDTO(datas=students)


@app.get("/hsc/classwise", response_model=List[StudentGroupwiseDTO])
def get_hsc_classwise(class_name: str, session: Session = Depends(get_session)):
    """Get HSC students filtered by class, ranked by total marks descending."""
    statement = (
        select(
            func.dense_rank().over(order_by=desc(HSC.total)).label("rank"),
            HSC.reg_no,
            HSC.class_.label("class_name"),
            HSC.group_name.label("group"),
            HSC.name,
            HSC.lang_name,
            HSC.lang,
            HSC.eng,
            HSC.sm1.label("sub1"),
            HSC.sm2.label("sub2"),
            HSC.sm3.label("sub3"),
            HSC.sm4.label("sub4"),
            HSC.total,
            HSC.cut_off.label("cutoff"),
        )
        .where(HSC.class_ == class_name)
        .order_by(desc(HSC.total))
    )

    results = session.exec(statement).all()

    return [
        StudentGroupwiseDTO(
            rank=row.rank,
            reg_no=row.reg_no,
            class_=row.class_name,
            group=row.group,
            name=row.name,
            lang_name=row.lang_name,
            lang=row.lang,
            eng=row.eng,
            sub1=row.sub1,
            sub2=row.sub2,
            sub3=row.sub3,
            sub4=row.sub4,
            total=row.total,
            cutoff=row.cutoff,
        )
        for row in results
    ]


@app.get("/hsc/sections", response_model=List[SectionDTO])
def get_hsc_sections(session: Session = Depends(get_session)):
    """
    Return all available class sections (sec) together with the groups/streams (grp)
    that exist for students in that section.

    Data is derived from the HSC table (distinct class + group_name).
    Uses display names and short subject codes for frontend use.
    """
    statement = (
        select(
            HSC.class_.label("sec"),
            HSC.group_name.label("code"),
            HSC.sn1,
            HSC.sn2,
            HSC.sn3,
            HSC.sn4,
        )
        .distinct()
        .order_by(HSC.class_, HSC.group_name)
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

        display_name = GROUP_DISPLAY_NAMES.get(code, code.upper())

        g = GroupDTO(
            name=display_name,
            code=code,
            sub1=abbreviate_subject(row.sn1),
            sub2=abbreviate_subject(row.sn2),
            sub3=abbreviate_subject(row.sn3),
            sub4=abbreviate_subject(row.sn4) if row.sn4 else None,
        )
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

        toppers.append(
            TopperResponse(
                rank=current_rank,
                reg_no=student.reg_no,
                class_=student.class_,
                group=student.group_name,
                name=student.name,
                lang_name=student.lang_name,
                lang=student.lang,
                eng=student.eng,
                sub1=student.sm1,
                sub2=student.sm2,
                sub3=student.sm3,
                sub4=student.sm4,
                total=student_total,
                cutoff=student.cut_off,
            )
        )
        # Update previous total for the next iteration
        previous_total = student_total

    return toppers


@app.get("/hsc/subject-first-marks", response_model=List[SubjectFirstMarkResponse])
def get_subject_first_marks(session: Session = Depends(get_session)):
    # Raw SQL query to unpivot the subject columns, find max marks, and count achievers
    query = text("""
        WITH unpivoted_subjects AS (
            SELECT sn1 AS subject_name, sm1 AS mark FROM hsc WHERE sn1 IS NOT NULL
            UNION ALL
            SELECT sn2 AS subject_name, sm2 AS mark FROM hsc WHERE sn2 IS NOT NULL
            UNION ALL
            SELECT sn3 AS subject_name, sm3 AS mark FROM hsc WHERE sn3 IS NOT NULL
            UNION ALL
            SELECT sn4 AS subject_name, sm4 AS mark FROM hsc WHERE sn4 IS NOT NULL AND sm4 IS NOT NULL
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

    # Map raw SQL results directly to the Pydantic schema
    return [
        SubjectFirstMarkResponse(name=row["name"], mark=row["mark"], count=row["count"])
        for row in result
    ]


@app.get("/hsc/subject/toppers", response_model=List[TopperResponse])
def get_hsc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    """Get top students for a specific HSC subject."""
    # Map frontend subject names to model columns
    subject_map = {
        "lang": HSC.lang,
        "eng": HSC.eng,
        "sm1": HSC.sm1,
        "sm2": HSC.sm2,
        "sm3": HSC.sm3,
        "sm4": HSC.sm4,
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
        student_mark = (
            getattr(student, subject_lower)
            if hasattr(student, subject_lower)
            else (getattr(student, subject_lower, 0))
        )

        if previous_mark is not None and student_mark < previous_mark:
            current_rank += 1

        toppers.append(
            TopperResponse(
                rank=current_rank,
                reg_no=student.reg_no,
                class_=student.class_,
                group=student.group_name,
                name=student.name,
                lang_name=student.lang_name,
                lang=student.lang,
                eng=student.eng,
                sub1=student.sm1,
                sub2=student.sm2,
                sub3=student.sm3,
                sub4=student.sm4,
                total=student.total if student.total is not None else 0,
                cutoff=student.cut_off,
            )
        )
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
                    group_name=group_name,
                    lang=int(row["TAMIL"]),
                    eng=int(row["ENGLISH"]),
                    sn1="PHYSICS",
                    sn2="CHEMISTRY",
                    sn3="COMPUTER SCIENCE",
                    sn4="MATHS",
                    sm1=physics,
                    sm2=chemistry,
                    sm3=comp_or_third,
                    sm4=maths,
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
    GET endpoint to read the new CSV file, parse the data,
    and insert rows into PostgreSQL using SQLModel.
    'total' and 'cut_off' are omitted so the database computes them via GENERATED ALWAYS AS.
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

            records_to_insert = []

            for row in reader:
                # Helper function to clear out empty string optional fields safely
                def get_optional_str(key: str) -> Optional[str]:
                    val = row.get(key)
                    if val is None:
                        return None
                    val = val.strip()
                    return val if val != "" else None

                # Helper function to parse optional int fields safely
                def get_optional_int(key: str) -> Optional[int]:
                    val = row.get(key)
                    if val is None:
                        return None
                    val = val.strip()
                    return int(val) if val != "" else None

                # Constructing the model instance directly using values from the CSV row
                hsc_record = HSC(
                    reg_no=int(row["reg_no"]),
                    class_=row["class"].strip(),
                    name=row["name"].strip(),
                    group_name=get_optional_str("group_name"),
                    lang_name=row["lang_name"].strip(),
                    lang=int(row["lang"]),
                    eng=int(row["eng"]),
                    sn1=row["sn1"].strip(),
                    sn2=row["sn2"].strip(),
                    sn3=row["sn3"].strip(),
                    sn4=get_optional_str("sn4"),
                    sm1=int(row["sm1"]),
                    sm2=int(row["sm2"]),
                    sm3=int(row["sm3"]),
                    sm4=get_optional_int("sm4"),
                    # cut_off (and total) are DB-generated via GENERATED ALWAYS AS — do not pass them
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
                "message": f"Successfully loaded {len(records_to_insert)} student records into the hsc table.",
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
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while writing to the database: {str(e)}",
        )
