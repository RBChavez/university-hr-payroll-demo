from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for
from functools import wraps
import sqlite3
import database
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'banner-extreme-secret-key-123'

# Config for File Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB on start
database.init_db()

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def log_audit(cursor, action, pidm=None, details=None):
    """Internal helper to log actions to GURUAUD"""
    # Use session user if available, fallback to 'system'
    audit_user = session.get('user', 'system')
    # Capture IP address from Flask request context
    ip_addr = request.remote_addr if request else '0.0.0.0'
    
    cursor.execute('''
        INSERT INTO GURUAUD (GURUAUD_PIDM, GURUAUD_ACTION, GURUAUD_USER, GURUAUD_IP, GURUAUD_DETAILS)
        VALUES (?, ?, ?, ?, ?)
    ''', (pidm, action, audit_user, ip_addr, details))

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == 'aomchavez' or username == 'guest') and password == 'admin':
            session['user'] = username
            
            # Log successful login
            conn = database.get_db_connection()
            log_audit(conn.cursor(), "LOGIN", None, f"User logged in from {request.remote_addr}")
            conn.commit()
            conn.close()
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/hire', methods=['GET'])
@login_required
def hire_page():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Dynamic values from PEBEMPL
    ecls_codes = cursor.execute('SELECT DISTINCT PEBEMPL_ECLS_CODE FROM PEBEMPL ORDER BY PEBEMPL_ECLS_CODE').fetchall()
    
    # Dynamic values from NBRJOBS
    classifications = cursor.execute('SELECT DISTINCT NBRJOBS_CLASSIFICATION FROM NBRJOBS WHERE NBRJOBS_CLASSIFICATION IS NOT NULL ORDER BY NBRJOBS_CLASSIFICATION').fetchall()
    categories = cursor.execute('SELECT DISTINCT NBRJOBS_JOB_CATEGORY FROM NBRJOBS WHERE NBRJOBS_JOB_CATEGORY IS NOT NULL ORDER BY NBRJOBS_JOB_CATEGORY').fetchall()
    locations = cursor.execute('SELECT DISTINCT NBRJOBS_LOCATION FROM NBRJOBS WHERE NBRJOBS_LOCATION IS NOT NULL ORDER BY NBRJOBS_LOCATION').fetchall()
    
    # Dynamic values from NTRPBND
    pay_bands = cursor.execute('SELECT NTRPBND_CODE, NTRPBND_MIN, NTRPBND_MAX FROM NTRPBND ORDER BY NTRPBND_CODE').fetchall()
    
    conn.close()
    
    return render_template('hire.html', 
                           ecls_codes=[row[0] for row in ecls_codes],
                           classifications=[row[0] for row in classifications],
                           categories=[row[0] for row in categories],
                           locations=[row[0] for row in locations],
                           pay_bands=[{'code': row[0], 'min': row[1], 'max': row[2]} for row in pay_bands])

@app.route('/payroll', methods=['GET'])
@login_required
def payroll_page():
    return render_template('payroll.html')

@app.route('/reports', methods=['GET'])
@login_required
def reports_page():
    return render_template('reports.html')

@app.route('/service', methods=['GET'])
@login_required
def service_page():
    return render_template('service.html')

@app.route('/audit', methods=['GET'])
@login_required
def audit_page():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    logs = cursor.execute('''
        SELECT g.*, s.SPRIDEN_FIRST_NAME, s.SPRIDEN_LAST_NAME 
        FROM GURUAUD g
        LEFT JOIN SPRIDEN s ON g.GURUAUD_PIDM = s.SPRIDEN_PIDM
        ORDER BY GURUAUD_ACTIVITY_DATE DESC
    ''').fetchall()
    conn.close()
    return render_template('audit.html', logs=logs)

@app.route('/employees', methods=['GET'])
@login_required
def employees_page():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Join tables to get Name, ID, Hiring Status, Job Title
    employees = cursor.execute('''
        SELECT s.SPRIDEN_ID as id, 
               s.SPRIDEN_LAST_NAME as last_name, 
               s.SPRIDEN_FIRST_NAME as first_name,
               p.PEBEMPL_EMPL_STATUS as status,
               p.PEBEMPL_ECLS_CODE as ecls,
               p.PEBEMPL_ORG_CODE_DIST as department,
               p.PEBEMPL_CURRENT_HIRE_DATE as hire_date,
               j.NBRJOBS_DESC as job_title,
               j.NBRJOBS_CLASSIFICATION as classification,
               j.NBRJOBS_JOB_CATEGORY as category,
               j.NBRJOBS_JOB_TYPE as job_type,
               j.NBRJOBS_LOCATION as location,
               j.NBRJOBS_WORKPLACE as workplace,
               j.NBRJOBS_PAY_BAND as pay_band,
               b.NBRBJOB_SALARY_ENCUMBRANCE as salary
        FROM SPRIDEN s
        JOIN PEBEMPL p ON s.SPRIDEN_PIDM = p.PEBEMPL_PIDM
        LEFT JOIN NBRJOBS j ON s.SPRIDEN_PIDM = j.NBRJOBS_PIDM 
                            AND j.NBRJOBS_STATUS = 'A'
        LEFT JOIN NBRBJOB b ON s.SPRIDEN_PIDM = b.NBRBJOB_PIDM
                            AND s.SPRIDEN_PIDM = b.NBRBJOB_PIDM
        ORDER BY s.SPRIDEN_LAST_NAME
    ''').fetchall()
    
    # Fetch Pay Band Rates for tooltips
    rates_data = cursor.execute('SELECT NTRPBND_CODE, NTRPBND_MIN, NTRPBND_MAX FROM NTRPBND').fetchall()
    pay_band_rates = {row[0]: f"${row[1]:,d} - ${row[2]:,d}" for row in rates_data}
    
    conn.close()

    dept_names = {
        '1100': 'Mathematics',
        '1200': 'Science', 
        '1300': 'Arts'
    }

    return render_template('employees.html', employees=employees, depts=dept_names, rates=pay_band_rates)

# --- API ENDPOINTS (Simulating PL/SQL Packages) ---

@app.route('/api/hire', methods=['POST'])
@login_required
def api_hire_employee():
    data = request.json
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert SPRIDEN
        cursor.execute('''
            INSERT INTO SPRIDEN (SPRIDEN_ID, SPRIDEN_LAST_NAME, SPRIDEN_FIRST_NAME, SPRIDEN_MI)
            VALUES (?, ?, ?, ?)
        ''', (data['banner_id'], data['last_name'], data['first_name'], data.get('mi', '')))
        
        pidm = cursor.lastrowid
        
        # 2. Insert PEBEMPL
        cursor.execute('''
            INSERT INTO PEBEMPL (PEBEMPL_PIDM, PEBEMPL_EMPL_STATUS, PEBEMPL_ECLS_CODE, 
                                 PEBEMPL_ORG_CODE_DIST, PEBEMPL_FIRST_HIRE_DATE, PEBEMPL_CURRENT_HIRE_DATE)
            VALUES (?, 'A', ?, ?, ?, ?)
        ''', (pidm, data['ecls'], data['orgn'], data['hire_date'], data['hire_date']))

        # 3. Assign Job (simplified for demo flow)
        cursor.execute('''
            INSERT INTO NBRJOBS (NBRJOBS_PIDM, NBRJOBS_POSN, NBRJOBS_SUFF, NBRJOBS_EFFECTIVE_DATE, 
                                 NBRJOBS_STATUS, NBRJOBS_DESC,
                                 NBRJOBS_CLASSIFICATION, NBRJOBS_JOB_CATEGORY, NBRJOBS_JOB_TYPE,
                                 NBRJOBS_LOCATION, NBRJOBS_WORKPLACE, NBRJOBS_PAY_BAND)
            VALUES (?, ?, '00', ?, 'A', ?, ?, ?, ?, ?, ?, ?)
        ''', (pidm, data['position'], data['hire_date'], data['job_title'], 
              data['classification'], data['category'], data['job_type'], 
              data['location'], data['workplace'], data['pay_band']))

        cursor.execute('''
            INSERT INTO NBRBJOB (NBRBJOB_PIDM, NBRBJOB_POSN, NBRBJOB_SUFF, NBRBJOB_BEGIN_DATE,
                                 NBRBJOB_SALARY_ENCUMBRANCE, NBRBJOB_CONTRACT_TYPE)
            VALUES (?, ?, '00', ?, ?, 'P')
        ''', (pidm, data['position'], data['hire_date'], data['salary']))

        log_audit(cursor, "HIRE_EMPLOYEE", pidm, f"Hired for position {data['position']} ({data['job_title']})")
        
        conn.commit()
        return jsonify({'status': 'success', 'pidm': pidm, 'message': 'Employee Hired & Job Assigned'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/employees/update', methods=['POST'])
@login_required
def api_update_employee():
    data = request.json
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        pidm = data['pidm']
        # 1. Update NBRJOBS (Job details)
        cursor.execute('''
            UPDATE NBRJOBS 
            SET NBRJOBS_DESC = ?, NBRJOBS_CLASSIFICATION = ?, NBRJOBS_JOB_CATEGORY = ?,
                NBRJOBS_JOB_TYPE = ?, NBRJOBS_LOCATION = ?, NBRJOBS_WORKPLACE = ?, NBRJOBS_PAY_BAND = ?
            WHERE NBRJOBS_PIDM = ? AND NBRJOBS_STATUS = 'A'
        ''', (data['job_title'], data['classification'], data['category'], 
              data['job_type'], data['location'], data['workplace'], data['pay_band'], pidm))

        # 2. Update NBRBJOB (Salary)
        cursor.execute('''
            UPDATE NBRBJOB 
            SET NBRBJOB_SALARY_ENCUMBRANCE = ?
            WHERE NBRBJOB_PIDM = ?
        ''', (data['salary'], pidm))

        log_audit(cursor, "EDIT_PROFILE", pidm, f"Updated job title to {data['job_title']} and salary to ${data['salary']}")
        
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/paybands', methods=['POST'])
@login_required
def api_add_payband():
    data = request.json
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO NTRPBND (NTRPBND_CODE, NTRPBND_MIN, NTRPBND_MAX)
            VALUES (?, ?, ?)
        ''', (data['code'], data['min'], data['max']))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/service/submit', methods=['POST'])
@login_required
def api_service_submit():
    # Handle both JSON and FormData
    if request.is_json:
        data = request.json
        service_type = data.get('type')
        subject = data.get('subject')
        details = data.get('details')
        priority = data.get('priority', 'Normal')
        contact = data.get('contact', 'Not provided')
        filename = None
    else:
        service_type = request.form.get('type')
        subject = request.form.get('subject')
        details = request.form.get('details')
        priority = request.form.get('priority', 'Normal')
        contact = request.form.get('contact', 'Not provided')
        
        # Handle file upload
        file = request.files.get('attachment')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        # Log the service request with contact info and attachment status
        audit_details = f"Contact: {contact} | Type: {service_type} | Subject: {subject} | Priority: {priority}"
        if filename:
            audit_details += f" | Attachment: {filename}"
            
        log_audit(cursor, "SERVICE_REQUEST", None, audit_details)
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Request submitted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/payroll', methods=['POST'])
@login_required
def api_run_payroll():
    # Helper to support 'view history' or 'run new'
    # Default is run new for current month if not specified
    data = request.json or {}
    mode = data.get('mode', 'new') 
    target_date = data.get('date', datetime.now().strftime("%Y-%m-%d"))

    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    results = []
    
    try:
        if mode == 'new':
            print(f"DEBUG: Starting payroll run for {target_date}")
            start_time = datetime.now()
            # 1. CALCULATE & SAVE
            # Fetch active jobs - added explicit join on POSN and SUFF to ensure correct mapping
            jobs = cursor.execute('''
                SELECT s.SPRIDEN_ID, s.SPRIDEN_PIDM, s.SPRIDEN_LAST_NAME, s.SPRIDEN_FIRST_NAME, 
                       b.NBRBJOB_SALARY_ENCUMBRANCE
                FROM NBRJOBS j
                JOIN NBRBJOB b ON j.NBRJOBS_PIDM = b.NBRBJOB_PIDM 
                              AND j.NBRJOBS_POSN = b.NBRBJOB_POSN
                              AND j.NBRJOBS_SUFF = b.NBRBJOB_SUFF
                JOIN SPRIDEN s ON j.NBRJOBS_PIDM = s.SPRIDEN_PIDM
                WHERE j.NBRJOBS_STATUS = 'A'
            ''').fetchall()
            
            print(f"DEBUG: Found {len(jobs)} jobs to process.")
            
            total_payroll = 0
            
            for job in jobs:
                salary = job['NBRBJOB_SALARY_ENCUMBRANCE']
                if salary:
                    monthly_gross = round(salary / 12, 2)
                    fed_tax = round(monthly_gross * 0.22, 2)
                    state_tax = round(monthly_gross * 0.0575, 2)
                    net_pay = monthly_gross - fed_tax - state_tax
                    
                    total_payroll += monthly_gross
                    
                    # Save to History
                    cursor.execute('''
                        INSERT OR REPLACE INTO PHRPAYRO (PHRPAYRO_PIDM, PHRPAYRO_EVENT_DATE, PHRPAYRO_GROSS_PAY, 
                                                         PHRPAYRO_FED_TAX, PHRPAYRO_STATE_TAX, PHRPAYRO_NET_PAY)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (job['SPRIDEN_PIDM'], target_date, monthly_gross, fed_tax, state_tax, net_pay))

                    results.append({
                        'id': job['SPRIDEN_ID'],
                        'name': f"{job['SPRIDEN_LAST_NAME']}, {job['SPRIDEN_FIRST_NAME']}",
                        'gross_pay': monthly_gross,
                        'fed_tax': fed_tax,
                        'state_tax': state_tax,
                        'net_pay': net_pay
                    })
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log_audit(cursor, "RUN_PAYROLL", None, f"Payroll period: {target_date}. Total: ${total_payroll:,.2f}. Duration: {duration:.2f}s")
            print(f"DEBUG: Payroll processed in {duration:.2f}s")
            conn.commit()
            
        else:
            # 2. VIEW HISTORY
            # Fetch from history table
            history = cursor.execute('''
                SELECT s.SPRIDEN_ID, s.SPRIDEN_LAST_NAME, s.SPRIDEN_FIRST_NAME, 
                       p.PHRPAYRO_GROSS_PAY, p.PHRPAYRO_FED_TAX, p.PHRPAYRO_STATE_TAX, p.PHRPAYRO_NET_PAY
                FROM PHRPAYRO p
                JOIN SPRIDEN s ON p.PHRPAYRO_PIDM = s.SPRIDEN_PIDM
                WHERE p.PHRPAYRO_EVENT_DATE = ?
            ''', (target_date,)).fetchall()
            
            total_payroll = 0
            for row in history:
                gross = row['PHRPAYRO_GROSS_PAY']
                total_payroll += gross
                results.append({
                    'id': row['SPRIDEN_ID'],
                    'name': f"{row['SPRIDEN_LAST_NAME']}, {row['SPRIDEN_FIRST_NAME']}",
                    'gross_pay': gross,
                    'fed_tax': row['PHRPAYRO_FED_TAX'],
                    'state_tax': row['PHRPAYRO_STATE_TAX'],
                    'net_pay': row['PHRPAYRO_NET_PAY']
                })

        return jsonify({
            'period': 'Historical View' if mode == 'view' else 'Current Run',
            'run_date': target_date,
            'total_processed': len(results),
            'total_expenditure': total_payroll,
            'details': results
        })

    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/payroll/dates', methods=['GET'])
def api_payroll_dates():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    dates = cursor.execute('SELECT DISTINCT PHRPAYRO_EVENT_DATE FROM PHRPAYRO ORDER BY PHRPAYRO_EVENT_DATE DESC').fetchall()
    conn.close()
    return jsonify([row[0] for row in dates])

@app.route('/api/stats', methods=['GET'])
def api_stats():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Headcount by Dept
    headcount = cursor.execute('''
        SELECT PEBEMPL_ORG_CODE_DIST, COUNT(*) as count 
        FROM PEBEMPL 
        WHERE PEBEMPL_EMPL_STATUS='A'
        GROUP BY PEBEMPL_ORG_CODE_DIST
    ''').fetchall()
    
    # Total Payroll estimate
    payroll = cursor.execute('''
        SELECT SUM(NBRBJOB_SALARY_ENCUMBRANCE) as total_annual
        FROM NBRBJOB
    ''').fetchone()

    # Salary Distribution
    salaries = cursor.execute('SELECT NBRBJOB_SALARY_ENCUMBRANCE FROM NBRBJOB WHERE NBRBJOB_SALARY_ENCUMBRANCE IS NOT NULL').fetchall()
    
    # Workplace Type Breakdown
    workforce = cursor.execute('SELECT NBRJOBS_WORKPLACE, COUNT(*) as count FROM NBRJOBS WHERE NBRJOBS_STATUS="A" GROUP BY NBRJOBS_WORKPLACE').fetchall()

    conn.close()
    
    # Map dept codes to names
    dept_map = {
        '1100': 'Mathematics',
        '1200': 'Science', 
        '1300': 'Arts'
    }

    formatted_headcount = []
    for row in headcount:
        d = dict(row)
        code = d.get('PEBEMPL_ORG_CODE_DIST')
        d['PEBEMPL_ORG_CODE_DIST'] = dept_map.get(code, code or 'Unassigned') 
        formatted_headcount.append(d)

    return jsonify({
        'headcount': formatted_headcount,
        'total_annual_payroll': payroll['total_annual'] if payroll['total_annual'] else 0,
        'salaries': [r[0] for r in salaries],
        'workplace_types': [dict(r) for r in workforce]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
