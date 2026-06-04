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
    cut_off real
);
