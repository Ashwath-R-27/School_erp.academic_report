import csv
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Session, SQLModel, select

from .database import engine, get_session
from .DTOs import TopperResponse
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
    for index, student in enumerate(results, start=1):
        student_total = student.total if student.total is not None else 0

        # If it's not the first student and the score dropped,
        # catch up the rank to the current loop position (Standard Competition Ranking / 1-2-2-4)
        if previous_total is not None and student_total < previous_total:
            current_rank = index

        toppers.append(
            TopperResponse(
                rank=current_rank,
                reg_no=student.reg_no,
                class_=student.class_,
                group=student.group_name,
                name=student.name,
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


@app.get("/hsc/subject/toppers")
def get_hsc_subject_toppers(
    subject: str, limit: int = 5, session: Session = Depends(get_session)
):
    # TODO: Get subject-specific toppers
    pass


# --- IMPORT HSC DATA ---
@app.get("/import_hsc")
def import_hsc_csv(
    file_path: str = "C:\\Users\\Asus\\Downloads\\result.csv",
    class_name: str = "XII-A1",
    group_name: str = "Computer Science",
    db: Session = Depends(get_session),
):
    """
    GET endpoint to read the CSV file, parse the data,
    calculate the engineering cut-off, and insert rows into PostgreSQL.
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
                maths = int(row["MATHS"])

                # Calculate Cut-off: Maths + (Physics / 2) + (Chemistry / 2)
                calculated_cutoff = float(maths + (physics / 2.0) + (chemistry / 2.0))

                hsc_record = HSC(
                    reg_no=int(row["REGNO"]),
                    class_=class_name,
                    name=row["NAME"].strip(),
                    group_name=group_name,
                    lang=int(row["TAMIL"]),
                    eng=int(row["ENGLISH"]),
                    sn1="PHYSICS",
                    sn2="CHEMISTRY",
                    sn3="COMP",
                    sn4="MATHS",
                    sm1=physics,
                    sm2=chemistry,
                    sm3=int(row["COMP"]),
                    sm4=maths,
                    cut_off=calculated_cutoff,
                    total=physics
                    + chemistry
                    + int(row["COMP"])
                    + maths
                    + int(row["TAMIL"])
                    + int(row["ENGLISH"]),
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
    file_path: str = "C:\\Users\\Asus\\Downloads\\result (1).csv",
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
                    total=int(row["TAMIL"])
                    + int(row["ENGLISH"])
                    + int(row["MATHS"])
                    + int(row["SCIENCE"])
                    + int(row["SOCIAL"]),
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
