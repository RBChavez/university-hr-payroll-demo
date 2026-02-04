
import requests
import json
import unittest

BASE_URL = "http://localhost:5000"

class TestHRPayroll(unittest.TestCase):
    def test_01_index(self):
        try:
            r = requests.get(BASE_URL)
            self.assertEqual(r.status_code, 200)
            print("Index page loaded.")
        except Exception as e:
            self.fail(f"Could not connect to server: {e}")

    def test_02_hire(self):
        import random
        rand_id = f"999{random.randint(10000, 99999)}"
        payload = {
            "banner_id": rand_id,
            "last_name": "TestUser",
            "first_name": "API",
            "mi": "X",
            "ecls": "FT",
            "orgn": "1100",
            "hire_date": "2026-02-01",
            "position": "PROF",
            "job_title": "Test Professor",
            "salary": 85000
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(f"{BASE_URL}/api/hire", json=payload, headers=headers)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['status'], 'success')
        print(f"Hired Employee PIDM: {data.get('pidm')}")

    def test_03_stats(self):
        r = requests.get(f"{BASE_URL}/api/stats")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        print("Stats:", data)
        self.assertIn('headcount', data)
        # Verify Dept Names are used
        depts = [d['PEBEMPL_ORG_CODE_DIST'] for d in data['headcount']]
        self.assertTrue(any(d in ['Mathematics', 'Science', 'Arts'] for d in depts))

    def test_04_payroll(self):
        # 1. Run New Payroll
        r = requests.post(f"{BASE_URL}/api/payroll", json={'mode': 'new'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        print("Payroll Run (New):", data['run_date'])
        self.assertTrue(data['total_processed'] > 0)
        
        # 2. View History
        target_date = data['run_date']
        r2 = requests.post(f"{BASE_URL}/api/payroll", json={'mode': 'view', 'date': target_date})
        self.assertEqual(r2.status_code, 200)
        history_data = r2.json()
        print("Payroll History (View):", history_data['run_date'])
        
        # Verify details match
        self.assertEqual(data['total_expenditure'], history_data['total_expenditure'])
        self.assertEqual(len(data['details']), len(history_data['details']))

if __name__ == '__main__':
    unittest.main()
