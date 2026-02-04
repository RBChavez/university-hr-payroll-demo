-- =============================================
-- Script: prc_extract_active_employees.sql
-- Description: Extract process for Active Employees to external systems (e.g., IAM, LMS).
--              Simulates generating a flat file.
-- Author: HR/Payroll Developer
-- Date: 2026-02-03
-- =============================================

CREATE OR REPLACE PROCEDURE PRC_EXTRACT_ACTIVE_EMPLOYEES AS
    CURSOR c_extract IS
        SELECT 
            s.SPRIDEN_ID AS EMP_ID,
            s.SPRIDEN_LAST_NAME AS LAST_NAME,
            s.SPRIDEN_FIRST_NAME AS FIRST_NAME,
            p.PEBEMPL_ECLS_CODE AS EMP_CLASS,
            p.PEBEMPL_ORG_CODE_DIST AS DEPT_CODE,
            s.SPRIDEN_ENTITY_IND AS TYPE
        FROM PEBEMPL p
        JOIN SPRIDEN s 
          ON p.PEBEMPL_PIDM = s.SPRIDEN_PIDM
        WHERE p.PEBEMPL_EMPL_STATUS = 'A'
          AND s.SPRIDEN_CHANGE_IND IS NULL
        ORDER BY s.SPRIDEN_LAST_NAME, s.SPRIDEN_FIRST_NAME;
        
    v_record_count NUMBER := 0;
    v_extract_line VARCHAR2(4000);
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- START OF EXTRACT ---');
    DBMS_OUTPUT.PUT_LINE('EMP_ID|LAST_NAME|FIRST_NAME|CLASS|DEPT|TYPE');
    
    FOR r IN c_extract LOOP
        -- Concatenate fields with pipe delimiter
        v_extract_line := r.EMP_ID || '|' || 
                          r.LAST_NAME || '|' || 
                          r.FIRST_NAME || '|' || 
                          r.EMP_CLASS || '|' || 
                          r.DEPT_CODE || '|' || 
                          r.TYPE;
                          
        DBMS_OUTPUT.PUT_LINE(v_extract_line);
        v_record_count := v_record_count + 1;
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('--- END OF EXTRACT ---');
    DBMS_OUTPUT.PUT_LINE('Total Records Extracted: ' || v_record_count);
    
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error in PRC_EXTRACT_ACTIVE_EMPLOYEES: ' || SQLERRM);
END PRC_EXTRACT_ACTIVE_EMPLOYEES;
/
