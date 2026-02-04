-- =============================================
-- Package: PKG_HR_MAINTENANCE
-- Description: API for HR processes including Onboarding and Maintenance.
-- Author: HR/Payroll Developer
-- Date: 2026-02-03
-- =============================================

CREATE OR REPLACE PACKAGE PKG_HR_MAINTENANCE AS

    -- Exception for invalid operations
    E_INVALID_HIRE_DATE EXCEPTION;
    PRAGMA EXCEPTION_INIT(E_INVALID_HIRE_DATE, -20001);

    -- Function to check hire eligibility
    -- Returns: 'Y' if eligible, 'N' otherwise
    FUNCTION IS_ELIGIBLE_FOR_HIRE (
        p_pidm IN NUMBER
    ) RETURN VARCHAR2;

    -- Procedure to hire a new employee
    -- Inserts into SPRIDEN and PEBEMPL
    PROCEDURE HIRE_EMPLOYEE (
        p_id            IN VARCHAR2,  -- Banner ID
        p_last_name     IN VARCHAR2,
        p_first_name    IN VARCHAR2,
        p_mi            IN VARCHAR2,
        p_hire_date     IN DATE,
        p_ecls          IN VARCHAR2,  -- Employee Class
        p_orgn          IN VARCHAR2,  -- Home Dept
        p_pidm_out      OUT NUMBER
    );

    -- Procedure to assign a job (simplified NBAJOBS)
    PROCEDURE ASSIGN_JOB (
        p_pidm          IN NUMBER,
        p_posn          IN VARCHAR2,
        p_suff          IN VARCHAR2,
        p_eff_date      IN DATE,
        p_title         IN VARCHAR2,
        p_salary        IN NUMBER
    );

END PKG_HR_MAINTENANCE;
/

CREATE OR REPLACE PACKAGE BODY PKG_HR_MAINTENANCE AS

    FUNCTION IS_ELIGIBLE_FOR_HIRE (
        p_pidm IN NUMBER
    ) RETURN VARCHAR2 IS
        v_dummy VARCHAR2(1);
    BEGIN
        -- Business Rule: Check if person exists and is not already active employee
        -- Simplified logic for demo
        BEGIN
            SELECT 'X' INTO v_dummy
            FROM PEBEMPL
            WHERE PEBEMPL_PIDM = p_pidm
              AND PEBEMPL_EMPL_STATUS = 'A';
            
            RETURN 'N'; -- Already active
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                RETURN 'Y';
        END;
    END IS_ELIGIBLE_FOR_HIRE;

    PROCEDURE HIRE_EMPLOYEE (
        p_id            IN VARCHAR2,
        p_last_name     IN VARCHAR2,
        p_first_name    IN VARCHAR2,
        p_mi            IN VARCHAR2,
        p_hire_date     IN DATE,
        p_ecls          IN VARCHAR2,
        p_orgn          IN VARCHAR2,
        p_pidm_out      OUT NUMBER
    ) IS
        v_pidm NUMBER;
    BEGIN
        -- Generate new PIDM
        SELECT SATURN_PIDM_SEQ.NEXTVAL INTO v_pidm FROM DUAL;
        p_pidm_out := v_pidm;

        -- Insert into SPRIDEN
        INSERT INTO SPRIDEN (
            SPRIDEN_PIDM, SPRIDEN_ID, SPRIDEN_LAST_NAME, SPRIDEN_FIRST_NAME, SPRIDEN_MI, SPRIDEN_CHANGE_IND
        ) VALUES (
            v_pidm, p_id, p_last_name, p_first_name, p_mi, NULL
        );

        -- Insert into PEBEMPL
        INSERT INTO PEBEMPL (
            PEBEMPL_PIDM, PEBEMPL_EMPL_STATUS, PEBEMPL_ECLS_CODE, PEBEMPL_ORG_CODE_DIST, 
            PEBEMPL_FIRST_HIRE_DATE, PEBEMPL_CURRENT_HIRE_DATE, PEBEMPL_ACTIVITY_DATE
        ) VALUES (
            v_pidm, 'A', p_ecls, p_orgn, p_hire_date, p_hire_date, SYSDATE
        );
        
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Employee Hired Successfully: PIDM ' || v_pidm);
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20010, 'Error in HIRE_EMPLOYEE: ' || SQLERRM);
    END HIRE_EMPLOYEE;

    PROCEDURE ASSIGN_JOB (
        p_pidm          IN NUMBER,
        p_posn          IN VARCHAR2,
        p_suff          IN VARCHAR2,
        p_eff_date      IN DATE,
        p_title         IN VARCHAR2,
        p_salary        IN NUMBER
    ) IS
    BEGIN
        -- Insert into NBRJOBS
        INSERT INTO NBRJOBS (
            NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE, 
            NBRJOBS_STATUS, NBRJOBS_DESC, NBRJOBS_ECLS_CODE
        ) VALUES (
            p_pidm, p_posn, p_suff, p_eff_date, 
            'A', p_title, NULL
        );

        -- Insert into NBRBJOB (Payroll dummy record)
        INSERT INTO NBRBJOB (
            NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE,
            NBRBJOB_SALARY_ENCUMBRANCE, NBRBJOB_CONTRACT_TYPE
        ) VALUES (
            p_pidm, p_posn, p_suff, p_eff_date,
            p_salary, 'P'
        );

        COMMIT;
    END ASSIGN_JOB;

END PKG_HR_MAINTENANCE;
/
