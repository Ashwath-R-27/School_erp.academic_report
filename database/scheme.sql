-- ============================================
-- Core Tables (matching the provided ER diagram)
-- ============================================

CREATE TABLE sslc (
    reg_no  integer PRIMARY KEY,
    class   varchar(2),
    name    varchar(30),
    tamil   integer,
    english integer,
    maths   integer,
    science integer,
    social  integer,
    total   integer GENERATED ALWAYS AS (
                tamil + english + maths + science + social
            ) STORED,
    result varchar(4)
);

-- Groups / Streams (CSC, BIOMAT, BIOCS, etc.)
CREATE TABLE groups (
    group_id  integer PRIMARY KEY,
    code      varchar(20) UNIQUE NOT NULL,   -- short code e.g. 'csc', 'biomat'
    name      varchar NOT NULL,              -- display name e.g. "COMPUTER SCIENCE + MATHS"
    subject1  varchar,
    subject2  varchar,
    subject3  varchar,
    subject4  varchar
);

-- HSC Marks (one row per student)
CREATE TABLE hsc (
    reg_no     integer PRIMARY KEY,
    class      varchar,
    name       varchar,

    -- Relationship to groups
    group_id   integer REFERENCES groups(group_id),

    -- group_code is denormalized here so we can use a pure GENERATED column for cut_off
    -- (GENERATED columns cannot reference other tables)
    group_code varchar(20),

    lang_name  varchar,
    lang       integer,
    eng        integer,

    -- Marks are now generic (meaning comes from the linked group)
    mark_1     integer,
    mark_2     integer,
    mark_3     integer,
    mark_4     integer,

    -- Core business logic preserved as DB-generated columns
    total      integer GENERATED ALWAYS AS (
                   lang + eng + mark_1 + mark_2 + mark_3 + mark_4
               ) STORED,

    cut_off    real GENERATED ALWAYS AS (
                   CASE
                       WHEN LOWER(group_code) IN ('csc', 'bme', 'biomat')
                       THEN ((mark_2 + mark_3) / 2.0) + mark_1
                       ELSE NULL
                   END
               ) STORED,
               result varchar(4)
);

-- Application users (new in the diagram)
CREATE TABLE users (
    id       uuid PRIMARY KEY,
    name     varchar,
    password varchar,
    email    varchar,
    phno     integer,
    class    varchar[],
    subject  varchar[]
);

-- ============================================
-- Student Registration Data (form submissions)
-- These tables store basic student details collected via forms
-- before marks are entered into the main sslc / hsc tables.
-- ============================================

CREATE TABLE sslc_student_data (
    reg_no integer PRIMARY KEY,
    name   varchar(30),
    class  varchar(2),
    dob    date
);

CREATE TABLE hsc_student_data (
    reg_no     integer PRIMARY KEY,
    name       varchar(30),
    class      varchar(2),
    dob        date,
    group_code varchar(6)
);

-- ============================================
-- Seed data for groups table (safe to re-run)
-- ============================================

INSERT INTO groups (group_id, code, name, subject1, subject2, subject3, subject4)
VALUES
    (1, 'csc',   'COMPUTER SCIENCE + MATHS',     'PHY', 'CHEM', 'CSC', 'MATHS'),
    (2, 'biomat','BIOLOGY + MATHS',              'PHY', 'CHEM', 'BIO', 'MATHS'),
    (3, 'biocs', 'BIOLOGY + COMPUTER SCIENCE',   'PHY', 'CHEM', 'BIO', 'CSC'),
    (4, 'artsca','ARTS + COMPUTER APPLICATION',  'ECO', 'COM', 'ACC', 'CA'),
    (5, 'artsbm','ARTS + BUSINESS MATHEMATICS',  'ECO', 'COM', 'ACC', 'BM'),
    (6, 'bme',   'BASIC MECHANICAL ENGINEERING', 'MATHS', 'BME (THY)', 'BME (PRT)', 'ES')
ON CONFLICT (group_id) DO UPDATE SET
    code = EXCLUDED.code,
    name = EXCLUDED.name,
    subject1 = EXCLUDED.subject1,
    subject2 = EXCLUDED.subject2,
    subject3 = EXCLUDED.subject3,
    subject4 = EXCLUDED.subject4;

-- ============================================
-- Notes:
-- - Total and cut_off use GENERATED ALWAYS AS (same business rules as before)
-- - Cut-off formula: for csc/biomat groups → (mark_2 + mark_3)/2 + mark_1
-- - mark_1..mark_4 order matches each group's subject1..subject4
-- - biocs subjects: BIOLOGY, CHEMISTRY, PHYSICS, CSC
-- - Subject names moved to the groups table (no longer stored per student)
-- - group_code kept in hsc only to support the generated cut_off expression
-- ============================================
