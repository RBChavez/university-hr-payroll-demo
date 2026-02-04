-- =============================================
-- Package: PKG_PAYROLL_CALC
-- Description: Core payroll processing logic.
-- Author: HR/Payroll Developer
-- Date: 2026-02-03
-- =============================================

CREATE OR REPLACE PACKAGE PKG_PAYROLL_CALC AS

    -- Procedure to calculate payroll for a given period
    -- Populates a mock payroll result table (which we simulate via output)
    PROCEDURE CALCULATE_PAYROLL (
        p_pay_period    IN VARCHAR2, -- e.g., '2026-MN01'
        p_process_date  IN DATE DEFAULT SYSDATE
    );

    -- Function to validate tax compliance (Placeholder)
    FUNCTION VAL_TAX_COMPLIANCE (
        p_pidm          IN NUMBER,
        p_net_pay       IN NUMBER
    ) RETURN BOOLEAN;

END PKG_PAYROLL_CALC;
/

CREATE OR REPLACE PACKAGE BODY PKG_PAYROLL_CALC AS

    FUNCTION VAL_TAX_COMPLIANCE (
        p_pidm          IN NUMBER,
        p_net_pay       IN NUMBER
    ) RETURN BOOLEAN IS
    BEGIN
        -- Simple compliance check: Net pay cannot be negative
        IF p_net_pay < 0 THEN
            RETURN FALSE;
        END IF;
        RETURN TRUE;
    END VAL_TAX_COMPLIANCE;

    PROCEDURE CALCULATE_PAYROLL (
        p_pay_period    IN VARCHAR2,
        p_process_date  IN DATE DEFAULT SYSDATE
    ) IS
        CURSOR c_active_jobs IS
            SELECT j.NBRJOBS_PIDM, j.NBRJOBS_POSN, j.NBRJOBS_SUFF, b.NBRBJOB_SALARY_ENCUMBRANCE
            FROM NBRJOBS j
            JOIN NBRBJOB b 
              ON j.NBRJOBS_PIDM = b.NBRBJOB_PIDM
             AND j.NBRJOBS_POSN = b.NBRBJOB_POSN
             AND j.NBRJOBS_SUFF = b.NBRBJOB_SUFF
            WHERE j.NBRJOBS_STATUS = 'A'
              AND b.NBRBJOB_CONTRACT_TYPE = 'P';
              
        v_monthly_gross NUMBER;
        v_processed_count NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting Payroll Calculation for Period: ' || p_pay_period);
        
        FOR r_job IN c_active_jobs LOOP
            -- logic: Annual Salary / 12
            IF r_job.NBRBJOB_SALARY_ENCUMBRANCE IS NOT NULL THEN
                v_monthly_gross := r_job.NBRBJOB_SALARY_ENCUMBRANCE / 12;
                
                -- Compliance Check
                IF VAL_TAX_COMPLIANCE(r_job.NBRJOBS_PIDM, v_monthly_gross) THEN
                    DBMS_OUTPUT.PUT_LINE('  Processed PIDM: ' || r_job.NBRJOBS_PIDM || 
                                         ' | Gross Pay: $' || ROUND(v_monthly_gross, 2));
                    v_processed_count := v_processed_count + 1;
                ELSE
                     DBMS_OUTPUT.PUT_LINE('  ERROR: Compliance Failure for PIDM: ' || r_job.NBRJOBS_PIDM);
                END IF;
            END IF;
        END LOOP;
        
        DBMS_OUTPUT.PUT_LINE('Payroll Completed. Total Employees Processed: ' || v_processed_count);
    END CALCULATE_PAYROLL;

END PKG_PAYROLL_CALC;
/
