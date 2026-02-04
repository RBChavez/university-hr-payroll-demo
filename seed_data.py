import sqlite3
import random
from datetime import datetime, timedelta
import sys
import os

# Add app directory to path so we can import database
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
import database

def seed_data():
    print("Initializing database...")
    database.init_db()
    print("Seeding database with mock employees...")
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Data pool
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    roles = [
        ("PROF", "Professor", 85000),
        ("ADMN", "Administrator", 65000),
        ("CUST", "Custodian", 35000),
        ("IT", "IT Specialist", 75000),
        ("HR", "HR Coordinator", 55000)
    ]
    statuses = ["A", "A", "A", "A", "A", "A", "T", "T", "L", "P"] # Weighted towards Active
    
    # New Field Options
    classifications = ['Info Technology Spec 3', 'Admin Asst 2', 'Faculty Rank 1', 'Fiscal Tech 3']
    categories = ['Classified Staff', 'University Staff', 'Faculty', 'Wage']
    job_types = ['Full-Time', 'Part-Time']
    locations = ['Fairfax, VA', 'Arlington, VA', 'Manassas, VA']
    workplaces = ['Remote', 'Hybrid', 'On-Site']
    pay_bands = ['04', '05', '06', '07']

    # Helper to generate common job data
    def get_job_details():
        return (
            random.choice(classifications),
            random.choice(categories),
            random.choice(job_types),
            random.choice(locations),
            random.choice(workplaces),
            random.choice(pay_bands)
        )

    # Generate 10 employees
    for i in range(10):
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        banner_id = f"999{random.randint(100000, 999999)}" # 9 Digits
        
        # 1. SPRIDEN
        cursor.execute('''
            INSERT INTO SPRIDEN (SPRIDEN_ID, SPRIDEN_LAST_NAME, SPRIDEN_FIRST_NAME, SPRIDEN_MI)
            VALUES (?, ?, ?, ?)
        ''', (banner_id, l_name, f_name, random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
        pidm = cursor.lastrowid

        status = statuses[i]
        role_code, role_desc, base_salary = random.choice(roles)
        hire_date = (datetime.now() - timedelta(days=random.randint(30, 365*5))).strftime("%Y-%m-%d")

        # 2. PEBEMPL
        cursor.execute('''
            INSERT INTO PEBEMPL (PEBEMPL_PIDM, PEBEMPL_EMPL_STATUS, PEBEMPL_ECLS_CODE, 
                                 PEBEMPL_ORG_CODE_DIST, PEBEMPL_FIRST_HIRE_DATE, PEBEMPL_CURRENT_HIRE_DATE)
            VALUES (?, ?, 'FT', '1100', ?, ?)
        ''', (pidm, status, hire_date, hire_date))

        # 3. NBRJOBS (Primary Job)
        cls, cat, jtype, loc, wp, band = get_job_details()
        
        cursor.execute('''
            INSERT INTO NBRJOBS (NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE, 
                                 NBRJOBS_STATUS, NBRJOBS_DESC, 
                                 NBRJOBS_CLASSIFICATION, NBRJOBS_JOB_CATEGORY, NBRJOBS_JOB_TYPE,
                                 NBRJOBS_LOCATION, NBRJOBS_WORKPLACE, NBRJOBS_PAY_BAND)
            VALUES (?, ?, '00', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pidm, role_code, hire_date, status, role_desc, cls, cat, jtype, loc, wp, band))

        # 4. NBRBJOB (Payroll info - only if Active or Leave)
        if status in ['A', 'L', 'P']:
            cursor.execute('''
                INSERT INTO NBRBJOB (NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE,
                                     NBRBJOB_SALARY_ENCUMBRANCE, NBRBJOB_CONTRACT_TYPE)
                VALUES (?, ?, '00', ?, ?, 'P')
            ''', (pidm, role_code, hire_date, base_salary))
        
        if i == 0:
             print(f"Added {f_name} {l_name} ({banner_id})")

    # Generate 50 recent hires (last 6 months)
    print("Generating 50 recent hires...")
    for i in range(50):
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        banner_id = f"999{random.randint(100000, 999999)}" # 9 Digits
        
        # 1. SPRIDEN
        cursor.execute('''
            INSERT INTO SPRIDEN (SPRIDEN_ID, SPRIDEN_LAST_NAME, SPRIDEN_FIRST_NAME, SPRIDEN_MI)
            VALUES (?, ?, ?, ?)
        ''', (banner_id, l_name, f_name, random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
        pidm = cursor.lastrowid

        # Mostly active for recent hires
        status = 'A' if random.random() > 0.1 else 'P' 
        role_code, role_desc, base_salary = random.choice(roles)
        
        # Random date in last 6 months (approx 180 days)
        days_ago = random.randint(0, 180)
        hire_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Distribute across departments
        dept = random.choice(['1100', '1200', '1300'])

        # 2. PEBEMPL
        cursor.execute('''
            INSERT INTO PEBEMPL (PEBEMPL_PIDM, PEBEMPL_EMPL_STATUS, PEBEMPL_ECLS_CODE, 
                                 PEBEMPL_ORG_CODE_DIST, PEBEMPL_FIRST_HIRE_DATE, PEBEMPL_CURRENT_HIRE_DATE)
            VALUES (?, ?, 'FT', ?, ?, ?)
        ''', (pidm, status, dept, hire_date, hire_date))

        # 3. NBRJOBS (Primary Job)
        cls, cat, jtype, loc, wp, band = get_job_details()

        cursor.execute('''
            INSERT INTO NBRJOBS (NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE, 
                                 NBRJOBS_STATUS, NBRJOBS_DESC,
                                 NBRJOBS_CLASSIFICATION, NBRJOBS_JOB_CATEGORY, NBRJOBS_JOB_TYPE,
                                 NBRJOBS_LOCATION, NBRJOBS_WORKPLACE, NBRJOBS_PAY_BAND)
            VALUES (?, ?, '00', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pidm, role_code, hire_date, status, role_desc, cls, cat, jtype, loc, wp, band))

        # 4. NBRBJOB
        cursor.execute('''
            INSERT INTO NBRBJOB (NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE,
                                    NBRBJOB_SALARY_ENCUMBRANCE, NBRBJOB_CONTRACT_TYPE)
            VALUES (?, ?, '00', ?, ?, 'P')
        ''', (pidm, role_code, hire_date, base_salary))
        
        if i < 5:
            print(f"Added Recent Hire: {f_name} {l_name} ({banner_id})")

    # Seed Pay Bands
    pay_bands = [
        ('04', 35000, 55000),
        ('05', 45000, 65000),
        ('06', 55000, 85000),
        ('07', 75000, 100000)
    ]
    cursor.executemany('INSERT OR REPLACE INTO NTRPBND (NTRPBND_CODE, NTRPBND_MIN, NTRPBND_MAX) VALUES (?, ?, ?)', pay_bands)

    conn.commit()
    conn.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
