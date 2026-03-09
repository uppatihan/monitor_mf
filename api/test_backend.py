import unittest
import json
import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestBackendAPI(unittest.TestCase):
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    def setUp(self):
        # We assume the server is running on port 5000 for integration tests
        # If the server is not running, we catch the connection error
        pass

    def test_01_server_running(self):
        """Check if the backend server is reachable"""
        try:
            # Using gsheet-counts as a simple GET check
            response = requests.get(f"{self.BASE_URL}/api/gsheet-counts", timeout=5)
            # 200 is success, 500 means server is up but there's a config issue (which is fine for this connectivity test)
            if response.status_code in [200, 500]:
                print("\n[test_01: Success] - Server is OK")
            else:
                print(f"\n[test_01: Warning] - Server status {response.status_code}")
            
            self.assertIn(response.status_code, [200, 500])
        except Exception as e:
            print(f"\n[test_01: Failed] - Server is not reachable. Error: {e}")
            self.fail(f"Server is not running. Please run 'python api/backend_server.py' first.")

    def test_02_gsheet_counts_format(self):
        """Verify the structure of /api/gsheet-counts response"""
        response = requests.get(f"{self.BASE_URL}/api/gsheet-counts", timeout=10)
        self.assertEqual(response.status_code, 200, "GSHeet API should return 200")
        
        data = response.json()
        self.assertIn("success", data)
        if data["success"]:
            self.assertIn("count_f", data)
            self.assertIn("count_h", data)
            self.assertIn("diff", data)
            self.assertIsInstance(data["count_f"], int)
            self.assertIsInstance(data["diff"], int)
            print("[test_02: Success] - Google Sheet is OK")

    def test_03_login_missing_credentials(self):
        """Test login endpoint with missing data"""
        payload = {"username": ""}
        response = requests.post(f"{self.BASE_URL}/api/login", json=payload, timeout=5)
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "กรุณาส่ง Username และ Password มาให้ครบถ้วน")
        print("[test_03: Success] - Login validation is OK")

    def test_04_login_invalid_credentials(self):
        """Test login endpoint with incorrect credentials"""
        payload = {
            "username": "invalid_user_test",
            "password": "wrong_password"
        }
        response = requests.post(f"{self.BASE_URL}/api/login", json=payload, timeout=20)
        self.assertEqual(response.status_code, 200, f"Expected 200 but got {response.status_code}. Content: {response.text}")
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("ล็อกอินไม่สำเร็จ", data["message"])
        print("[test_04: Success] - Invalid credentials handled OK")

    # def test_05_multi_session_login(self):
    #     """Simulate two independent login attempts for the same user (multi-machine)"""
    #     payload = {
    #         "username": "multi_test_user",
    #         "password": "some_password"
    #     }
        
    #     # Simulate "Machine 1"
    #     print("\n[test_05] Starting Machine 1 Login...")
    #     response1 = requests.post(f"{self.BASE_URL}/api/login", json=payload, timeout=20)
    #     self.assertEqual(response1.status_code, 200)
        
    #     # Simulating time gap (e.g., login held for 5 seconds)
    #     print(f"[test_05] Holding Machine 1 session for 5 seconds...")
    #     time.sleep(5)
        
    #     # Simulate "Machine 2"
    #     print("[test_05] Starting Machine 2 Login while Machine 1 is active...")
    #     response2 = requests.post(f"{self.BASE_URL}/api/login", json=payload, timeout=20)
    #     self.assertEqual(response2.status_code, 200)
        
    #     # Verify both handled as independent requests
    #     data1 = response1.json()
    #     data2 = response2.json()
        
    #     self.assertIn("success", data1)
    #     self.assertIn("success", data2)
    #     print("[test_05: Success] - Multi-session login simulation handled OK")

if __name__ == "__main__":
    unittest.main()
