-- =============================================
-- Script: 01_mock_banner_schema.sql
-- Description: Creates mock tables simulating the Ellucian Banner HR Schema.
-- Author: HR/Payroll System Architect
-- Date: 2026-02-03
-- =============================================

-- 1. SPRIDEN: Person Identification (Commonly used in Banner)
-- Represents the core identity of a person (Students, Employees, Vendors, etc.)
CREATE TABLE SPRIDEN (
    SPRIDEN_PIDM        NUMBER(8)       NOT NULL, -- Internal unique ID
    SPRIDEN_ID          VARCHAR2(9)     NOT NULL, -- Public ID (e.g., University ID)
    SPRIDEN_LAST_NAME   VARCHAR2(60)    NOT NULL,
    SPRIDEN_FIRST_NAME  VARCHAR2(60)    NOT NULL,
    SPRIDEN_MI          VARCHAR2(60),
    SPRIDEN_CHANGE_IND  VARCHAR2(1),              -- Name change indicator
    SPRIDEN_ENTITY_IND  VARCHAR2(1) DEFAULT 'P',  -- P=Person, C=Company
    SPRIDEN_ACTIVITY_DATE DATE DEFAULT SYSDATE,
    CONSTRAINT PK_SPRIDEN PRIMARY KEY (SPRIDEN_PIDM, SPRIDEN_CHANGE_IND),
    CONSTRAINT UK_SPRIDEN_ID UNIQUE (SPRIDEN_ID)
);

COMMENT ON TABLE SPRIDEN IS 'Person Identification/Bio-Demo Data';

-- 2. PEBEMPL: Employee Base Table
-- Contains high-level employee attributes
CREATE TABLE PEBEMPL (
    PEBEMPL_PIDM        NUMBER(8)       NOT NULL,
    PEBEMPL_EMPL_STATUS VARCHAR2(1)     NOT NULL, -- A=Active, T=Terminated, L=Leave
    PEBEMPL_ECLS_CODE   VARCHAR2(2)     NOT NULL, -- Employee Class (e.g., FT, PT)
    PEBEMPL_ORG_CODE_DIST VARCHAR2(6),            -- Home Department
    PEBEMPL_FIRST_HIRE_DATE DATE        NOT NULL,
    PEBEMPL_CURRENT_HIRE_DATE DATE      NOT NULL,
    PEBEMPL_ADJ_SERVICE_DATE DATE,
    PEBEMPL_ACTIVITY_DATE DATE DEFAULT SYSDATE,
    CONSTRAINT PK_PEBEMPL PRIMARY KEY (PEBEMPL_PIDM),
    CONSTRAINT FK_PEBEMPL_SPRIDEN FOREIGN KEY (PEBEMPL_PIDM) 
        REFERENCES SPRIDEN (SPRIDEN_PIDM)
);

COMMENT ON TABLE PEBEMPL IS 'Employee General Information';

-- 3. PTRROLE: Role Validation Table
-- Lookup for Job Roles/Titles (simplification of Banner's position control)
CREATE TABLE PTRROLE (
    PTRROLE_CODE        VARCHAR2(6)     NOT NULL,
    PTRROLE_DESC        VARCHAR2(60)    NOT NULL,
    PTRROLE_ACTIVITY_DATE DATE DEFAULT SYSDATE,
    CONSTRAINT PK_PTRROLE PRIMARY KEY (PTRROLE_CODE)
);

INSERT INTO PTRROLE VALUES ('PROF', 'Professor', SYSDATE);
INSERT INTO PTRROLE VALUES ('ADMN', 'Administrator', SYSDATE);
INSERT INTO PTRROLE VALUES ('ITSP', 'IT Support', SYSDATE);
INSERT INTO PTRROLE VALUES ('HRGN', 'HR Generalist', SYSDATE);

-- 4. NBRJOBS: Employee Jobs Table (Base)
-- Defines the link between an employee and a position
CREATE TABLE NBRJOBS (
    NBRJOBS_PIDM        NUMBER(8)       NOT NULL,
    NBRJOBS_POSN        VARCHAR2(6)     NOT NULL, -- Position Number
    NBRJOBS_SUFF        VARCHAR2(2)     NOT NULL, -- Suffix
    NBRJOBS_EFFECTIVE_DATE DATE         NOT NULL,
    NBRJOBS_STATUS      VARCHAR2(1)     NOT NULL, -- A=Active, T=Terminated
    NBRJOBS_DESC        VARCHAR2(60),             -- Job Title Override
    NBRJOBS_ECLS_CODE   VARCHAR2(2),
    NBRJOBS_ACTIVITY_DATE DATE DEFAULT SYSDATE,
    CONSTRAINT PK_NBRJOBS PRIMARY KEY (NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE),
    CONSTRAINT FK_NBRJOBS_PEBEMPL FOREIGN KEY (NBRJOBS_PIDM) 
        REFERENCES PEBEMPL (PEBEMPL_PIDM)
);

COMMENT ON TABLE NBRJOBS IS 'Employee Job Definition';

-- 5. NBRBJOB: Job Detail/Payroll Info
-- Contains salary and detailed payroll configurations for the job
CREATE TABLE NBRBJOB (
    NBRBJOB_PIDM        NUMBER(8)       NOT NULL,
    NBRBJOB_POSN        VARCHAR2(6)     NOT NULL,
    NBRBJOB_SUFF        VARCHAR2(2)     NOT NULL,
    NBRBJOB_BEGIN_DATE  DATE            NOT NULL,
    NBRBJOB_END_DATE    DATE,
    NBRBJOB_CONTRACT_TYPE VARCHAR2(1),            -- P=Primary, S=Secondary
    NBRBJOB_SALARY_ENCUMBRANCE NUMBER(11,2),      -- Annual Salary
    NBRBJOB_HRLY_RATE   NUMBER(7,2),              -- Hourly Rate (if applicable)
    NBRBJOB_ACTIVITY_DATE DATE DEFAULT SYSDATE,
    CONSTRAINT PK_NBRBJOB PRIMARY KEY (NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE),
    CONSTRAINT FK_NBRBJOB_NBRJOBS FOREIGN KEY (NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE)
        REFERENCES NBRJOBS (NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE)
);

COMMENT ON TABLE NBRBJOB IS 'Base Job Payroll Details';

-- Sequence for PIDM Generation (Banner usually uses sequences)
CREATE SEQUENCE SATURN_PIDM_SEQ START WITH 10001 INCREMENT BY 1;
