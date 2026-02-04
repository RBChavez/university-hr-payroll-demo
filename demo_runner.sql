-- =============================================
-- Script: demo_runner.sql
-- Description: End-to-End Demo of the University HR Payroll System.
--              Run this script in an Oracle Environment to verify functionality.
-- =============================================

SET SERVEROUTPUT ON;
SET ECHO OFF;

PROMPT =================================================;
PROMPT UNIT TESTING: UNIVERSITY HR PAYROLL SYSTEM;
PROMPT =================================================;

-- 1. Setup Environment (Clean up previous runs if needed - optional)
-- DROP TABLE SPRIDEN PURGE; ... (Omitted for safety)

-- 2. Test Hiring an Employee
PROMPT [STEP 1] Hiring New Employee: John Doe...

DECLARE
    v_pidm NUMBER;
BEGIN
    PKG_HR_MAINTENANCE.HIRE_EMPLOYEE(
        p_id            => 'U00000001',
        p_last_name     => 'Doe',
        p_first_name    => 'John',
        p_mi            => 'A',
        p_hire_date     => SYSDATE,
        p_ecls          => 'FT', -- Full Time
        p_orgn          => 'IT001',
        p_pidm_out      => v_pidm
    );
    
    -- Assign this PIDM to a bind variable or temporary storage for next steps if needed
    -- For this script block, we continue using v_pidm
    
    PROMPT [STEP 2] Assigning Job: Professor...
    PKG_HR_MAINTENANCE.ASSIGN_JOB(
        p_pidm          => v_pidm,
        p_posn          => 'P00100',
        p_suff          => '00',
        p_eff_date      => SYSDATE,
        p_title         => 'Senior Professor',
        p_salary        => 95000
    );
    
END;
/

-- 3. Run Payroll Calculation
PROMPT [STEP 3] Running Payroll Process for Current Month...
EXEC PKG_PAYROLL_CALC.CALCULATE_PAYROLL('2026-FEB', SYSDATE);

-- 4. Verify Integrations
PROMPT [STEP 4] Executing Active Employee Extract (Mock Output)...
EXEC PRC_EXTRACT_ACTIVE_EMPLOYEES;

-- 5. Verify Reporting Views
PROMPT [STEP 5] Querying HR Analytics Views...

PROMPT >> Headcount Report:
SELECT * FROM HR_HEADCOUNT_V;

PROMPT >> Payroll Expenditure Report:
SELECT * FROM PAYROLL_EXPENDITURE_V;

PROMPT >> Detailed Employee View:
SELECT * FROM HR_EMPLOYEE_DETAIL_V;

PROMPT =================================================;
PROMPT DEMO COMPLETED SUCCESSFULLY.;
PROMPT =================================================;
