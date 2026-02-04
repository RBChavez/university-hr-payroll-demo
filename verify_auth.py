import requests
import time

def verify_auth():
    print("Waiting for server...")
    time.sleep(5)
    
    session = requests.Session()
    base_url = "http://localhost:5000"
    
    # 1. Attempt access without login
    r_unauth = session.get(f"{base_url}/employees", allow_redirects=False)
    print(f"Directory access without login (Status 302/redirect expected): {r_unauth.status_code}")
    
    # 2. Login with correct credentials
    login_data = {'username': 'aomchavez', 'password': 'admin'}
    r_login = session.post(f"{base_url}/login", data=login_data)
    print(f"Login with aomchavez/admin (Redirect to index expected 200 after redirect): {r_login.status_code}")
    print(f"Access granted to Directory after login: {'Employee Directory' in r_login.text or r_login.url.endswith('/employees')}")
    
    # 3. Access sensitive route after login
    r_hire = session.get(f"{base_url}/hire")
    print(f"Access to /hire after login: {'New Hire Onboarding' in r_hire.text}")
    
    # 4. Logout
    session.get(f"{base_url}/logout")
    r_post_logout = session.get(f"{base_url}/employees", allow_redirects=False)
    print(f"Directory access after logout (Status 302 expected): {r_post_logout.status_code}")

if __name__ == "__main__":
    verify_auth()
