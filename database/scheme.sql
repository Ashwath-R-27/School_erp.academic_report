
CREATE TABLE sslc_result (
    reg_no integer PRIMARY KEY,
    class varchar(1),
    first_name varchar(15),
    last_name varchar(15),
    tamil integer,
    english integer,
    maths integer,
    science integer,
    social integer,
    total integer GENERATED ALWAYS AS (tamil + english + maths + science + social) STORED,
);

CREATE TABLE hsc_result_cs (
    reg_no integer PRIMARY KEY,
    class varchar(1),
    first_name varchar(15),
    last_name varchar(15),
    lang integer,
    eng integer,
    phy integer,
    chem integer,
    csc integer,
    maths integer,
    total integer GENERATED ALWAYS AS (lang + eng + phy + chem + csc + maths) STORED,
    cut_off real
);

CREATE TABLE hsc_result_bio (
    reg_no integer PRIMARY KEY,
    class varchar(1),
    first_name varchar(15),
    last_name varchar(15),
    lang integer,
    eng integer,
    phy integer,
    chem integer,
    bio integer,
    maths integer,
    total integer GENERATED ALWAYS AS (lang + eng + phy + chem + bio + maths) STORED,
    cut_off real GENERATED ALWAYS AS (phy + chem + )
);
