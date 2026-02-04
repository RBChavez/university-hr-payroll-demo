import requests
import json

URL = "http://localhost:5000/api/payroll"

def verify():
    # API is not protected by @login_required, but session handles it if needed
    session = requests.Session()
    
    # Run new payroll
    print("Sending payroll request...")
    response = session.post(URL, json={"mode": "new"})
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Payroll processed.")
        print(f"Total Processed: {data['total_processed']}")
        print(f"Total Expenditure: {data['total_expenditure']}")
        if data['details']:
            first = data['details'][0]
            print(f"Sample Entry: {first['name']} (Gross: {first['gross_pay']}, Net: {first['net_pay']})")
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    verify()
