import time
import requests

def verify():
    print("Waiting for server...")
    time.sleep(5)
    
    # 1. Add New Pay Band
    pb_data = {'code': '10', 'min': 100000, 'max': 150000}
    try:
        r_pb = requests.post('http://localhost:5000/api/paybands', json=pb_data)
        print('Add PayBand Status:', r_pb.json().get('status'))
    except Exception as e:
        print('Failed to add Pay Band:', e)
        return

    # 2. Hire Employee with New Pay Band
    emp_data = {
        'banner_id': '999777111',
        'first_name': 'Pay',
        'last_name': 'BandTester',
        'ecls': 'AD',
        'orgn': 'TEST',
        'hire_date': '2024-02-03',
        'position': 'PTEST',
        'job_title': 'Band Verifier',
        'salary': 120000,
        'classification': 'Admin Asst 2',
        'category': 'University Staff',
        'job_type': 'Full-Time',
        'location': 'Fairfax, VA',
        'workplace': 'Hybrid',
        'pay_band': '10'
    }
    try:
        r_hire = requests.post('http://localhost:5000/api/hire', json=emp_data)
        print('Hire Status:', r_hire.json().get('status'))
    except Exception as e:
        print('Failed to hire employee:', e)
        return

    # 3. Check Directory Tooltip
    try:
        r_dir = requests.get('http://localhost:5000/employees')
        tooltip_str = 'title="$100,000 - $150,000"'
        if tooltip_str in r_dir.text:
            print('New PayBand Tooltip in Directory: True')
        else:
            print('New PayBand Tooltip in Directory: False (Tooltip not found)')
            # Print a bit of the output for debugging if needed
            if 'BandTester' in r_dir.text:
                print('Employee found in directory.')
    except Exception as e:
        print('Failed to check directory:', e)

if __name__ == "__main__":
    verify()
