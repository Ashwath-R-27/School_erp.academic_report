CREATE TABLE sslc (
    reg_no integer PRIMARY KEY,
    class varchar(1),
    name varchar(30),
    tamil integer,
    english integer,
    maths integer,
    science integer,
    social integer,
    total integer GENERATED ALWAYS AS (tamil + english + maths + science + social) STORED
);

CREATE TABLE hsc (
    reg_no integer PRIMARY KEY,
    class varchar NOT NULL,
    name varchar NOT NULL,
    group_name varchar,
    lang_name varchar NOT NULL,
    lang integer NOT NULL,
    eng integer NOT NULL,
    sn1 varchar NOT NULL,
    sn2 varchar NOT NULL,
    sn3 varchar NOT NULL,
    sn4 varchar,
    sm1 integer NOT NULL,
    sm2 integer NOT NULL,
    sm3 integer NOT NULL,
    sm4 integer,
    total integer GENERATED ALWAYS AS (lang + eng + sm1 + sm2 + sm3 + sm4) STORED,
    cut_off real GENERATED ALWAYS AS (
        CASE
            WHEN LOWER(group_name) IN ('csc', 'biomat', 'bme')
            THEN ((sm2 + sm3) / 2.0) + sm1
            ELSE NULL
        END
    ) STORED

);

CREATE TABLE hsc_student_data (
    reg_no integer PRIMARY KEY,
    name varchar(30),
    class varchar(1),
    dob date,
    group_code varchar(6),

);

CREATE TABLE sslc_student_data (
    reg_no integer PRIMARY KEY,
    name varchar(30),
    class varchar(1),
    dob date
);
