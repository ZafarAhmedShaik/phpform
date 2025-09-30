#!/usr/bin/env python3
"""
Backend API Testing Suite for Client Form Management System
Tests all backend endpoints with comprehensive scenarios
"""

import requests
import json
import csv
import io
from datetime import datetime
import hashlib

# Configuration
BACKEND_URL = "https://php-form-portal.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def hash_password(self, password):
        """Hash password same way as backend"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root Endpoint", True, "API root accessible", data)
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Unexpected response format", response.text)
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_client_submission_valid(self):
        """Test client form submission with valid data"""
        test_data = {
            "full_name": "John Smith",
            "email": f"john.smith.{datetime.now().timestamp()}@example.com",  # Unique email
            "phone_number": "+1234567890"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/clients",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "full_name", "email", "phone_number", "submitted_at"]
                if all(field in data for field in required_fields):
                    self.log_test("Client Submission (Valid)", True, "Successfully submitted client data", data)
                    return True, data
                else:
                    self.log_test("Client Submission (Valid)", False, "Missing required fields in response", data)
                    return False, None
            else:
                self.log_test("Client Submission (Valid)", False, f"HTTP {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Client Submission (Valid)", False, f"Request error: {str(e)}")
            return False, None
    
    def test_client_submission_duplicate_email(self):
        """Test client form submission with duplicate email"""
        # First submission
        test_data = {
            "full_name": "Jane Doe",
            "email": "duplicate.test@example.com",
            "phone_number": "+1987654321"
        }
        
        try:
            # Submit first time
            response1 = self.session.post(
                f"{BACKEND_URL}/clients",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Submit second time with same email
            response2 = self.session.post(
                f"{BACKEND_URL}/clients",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response2.status_code == 400:
                error_data = response2.json()
                if "already registered" in error_data.get("detail", "").lower():
                    self.log_test("Client Submission (Duplicate Email)", True, "Correctly rejected duplicate email", error_data)
                    return True
                else:
                    self.log_test("Client Submission (Duplicate Email)", False, "Wrong error message for duplicate", error_data)
                    return False
            else:
                self.log_test("Client Submission (Duplicate Email)", False, f"Expected 400, got {response2.status_code}", response2.text)
                return False
        except Exception as e:
            self.log_test("Client Submission (Duplicate Email)", False, f"Request error: {str(e)}")
            return False
    
    def test_client_submission_validation_errors(self):
        """Test client form submission with validation errors"""
        test_cases = [
            {
                "name": "Short name",
                "data": {"full_name": "A", "email": "test@example.com", "phone_number": "+1234567890"},
                "expected_error": "min_length"
            },
            {
                "name": "Invalid email",
                "data": {"full_name": "John Doe", "email": "invalid-email", "phone_number": "+1234567890"},
                "expected_error": "email"
            },
            {
                "name": "Short phone",
                "data": {"full_name": "John Doe", "email": "test@example.com", "phone_number": "123"},
                "expected_error": "min_length"
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/clients",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 422:  # Validation error
                    self.log_test(f"Validation ({test_case['name']})", True, "Correctly rejected invalid data", response.json())
                else:
                    self.log_test(f"Validation ({test_case['name']})", False, f"Expected 422, got {response.status_code}", response.text)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Validation ({test_case['name']})", False, f"Request error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "message" in data:
                    self.admin_token = data["access_token"]
                    self.log_test("Admin Login (Success)", True, "Successfully logged in", {"token_length": len(self.admin_token)})
                    return True
                else:
                    self.log_test("Admin Login (Success)", False, "Missing token or message in response", data)
                    return False
            else:
                self.log_test("Admin Login (Success)", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Login (Success)", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_login_failure(self):
        """Test admin login with incorrect credentials"""
        login_data = {
            "username": "wrong_user",
            "password": "wrong_password"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_test("Admin Login (Failure)", True, "Correctly rejected invalid credentials", error_data)
                return True
            else:
                self.log_test("Admin Login (Failure)", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Login (Failure)", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_clients_retrieval(self):
        """Test admin client data retrieval"""
        if not self.admin_token:
            self.log_test("Admin Clients Retrieval", False, "No admin token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/admin/clients", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Admin Clients Retrieval", True, f"Retrieved {len(data)} client records", {"count": len(data)})
                    return True, data
                else:
                    self.log_test("Admin Clients Retrieval", False, "Response is not a list", data)
                    return False, None
            else:
                self.log_test("Admin Clients Retrieval", False, f"HTTP {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Admin Clients Retrieval", False, f"Request error: {str(e)}")
            return False, None
    
    def test_admin_clients_unauthorized(self):
        """Test admin client data retrieval without token"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 403:  # Forbidden without auth
                self.log_test("Admin Clients (Unauthorized)", True, "Correctly blocked unauthorized access", response.json())
                return True
            else:
                self.log_test("Admin Clients (Unauthorized)", False, f"Expected 403, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Clients (Unauthorized)", False, f"Request error: {str(e)}")
            return False
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        if not self.admin_token:
            self.log_test("CSV Export", False, "No admin token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}"
            }
            
            response = self.session.get(f"{BACKEND_URL}/admin/clients/export", headers=headers)
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    # Check content disposition
                    content_disposition = response.headers.get('content-disposition', '')
                    if 'attachment' in content_disposition and 'filename' in content_disposition:
                        # Try to parse CSV
                        csv_content = response.text
                        csv_reader = csv.reader(io.StringIO(csv_content))
                        rows = list(csv_reader)
                        
                        if len(rows) > 0:
                            header = rows[0]
                            expected_headers = ['ID', 'Full Name', 'Email', 'Phone Number', 'Submitted At']
                            if header == expected_headers:
                                self.log_test("CSV Export", True, f"Successfully exported CSV with {len(rows)-1} data rows", {
                                    "headers": header,
                                    "total_rows": len(rows),
                                    "content_type": content_type
                                })
                                return True
                            else:
                                self.log_test("CSV Export", False, "CSV headers don't match expected format", {
                                    "expected": expected_headers,
                                    "actual": header
                                })
                                return False
                        else:
                            self.log_test("CSV Export", False, "CSV file is empty")
                            return False
                    else:
                        self.log_test("CSV Export", False, "Missing proper content disposition header", response.headers)
                        return False
                else:
                    self.log_test("CSV Export", False, f"Wrong content type: {content_type}", response.headers)
                    return False
            else:
                self.log_test("CSV Export", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("CSV Export", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_stats(self):
        """Test admin dashboard statistics"""
        if not self.admin_token:
            self.log_test("Admin Stats", False, "No admin token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_clients", "recent_submissions"]
                if all(field in data for field in required_fields):
                    if isinstance(data["total_clients"], int) and isinstance(data["recent_submissions"], int):
                        self.log_test("Admin Stats", True, "Successfully retrieved statistics", data)
                        return True
                    else:
                        self.log_test("Admin Stats", False, "Statistics values are not integers", data)
                        return False
                else:
                    self.log_test("Admin Stats", False, "Missing required statistics fields", data)
                    return False
            else:
                self.log_test("Admin Stats", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Stats", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("BACKEND API TESTING SUITE")
        print("=" * 80)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"Admin credentials: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print("-" * 80)
        
        # Test sequence
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Client Submission (Valid)", self.test_client_submission_valid),
            ("Client Submission (Duplicate Email)", self.test_client_submission_duplicate_email),
            ("Client Validation Errors", self.test_client_submission_validation_errors),
            ("Admin Login (Success)", self.test_admin_login_success),
            ("Admin Login (Failure)", self.test_admin_login_failure),
            ("Admin Clients (Unauthorized)", self.test_admin_clients_unauthorized),
            ("Admin Clients Retrieval", self.test_admin_clients_retrieval),
            ("CSV Export", self.test_csv_export),
            ("Admin Stats", self.test_admin_stats)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['message']}")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    exit(0 if failed == 0 else 1)