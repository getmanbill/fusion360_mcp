"""
Comprehensive Angular Dimension Testing
Tests multiple scenarios, edge cases, and integration with other sketch operations
"""
import json
import socket
import time
import math
from datetime import datetime

class ComprehensiveAngularDimensionTester:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        self.test_results = {
            "test_suite": "comprehensive_angular_dimension",
            "timestamp": datetime.now().isoformat(),
            "scenarios": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "edge_cases_tested": 0
            }
        }
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(15.0)
            self.socket.connect((self.host, self.port))
            print("✅ Connected to MCP server")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def send_request(self, method: str, params: dict = None):
        if params is None:
            params = {}
            
        request = {
            "method": method,
            "params": params,
            "id": self.request_id
        }
        
        self.request_id += 1
        
        try:
            request_json = json.dumps(request) + '\n'
            self.socket.send(request_json.encode('utf-8'))
            
            response_data = b""
            timeout_counter = 0
            while timeout_counter < 50:  # 5 second timeout
                chunk = self.socket.recv(8192)
                if not chunk:
                    break
                response_data += chunk
                try:
                    response_str = response_data.decode('utf-8')
                    if response_str.strip().endswith('}'):
                        break
                except:
                    continue
                timeout_counter += 1
                time.sleep(0.1)
                    
            response = json.loads(response_data.decode('utf-8'))
            return response
            
        except Exception as e:
            return {"error": str(e)}

    def log_test_result(self, test_name: str, success: bool, details: dict):
        """Log individual test result"""
        self.test_results["scenarios"].append({
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        
        self.test_results["summary"]["total_tests"] += 1
        if success:
            self.test_results["summary"]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {details.get('error', 'Unknown error')}")

    def create_test_sketch(self, plane="XY"):
        """Helper to create a sketch for testing"""
        response = self.send_request('fusion.create_sketch', {"plane": plane})
        if 'error' in response:
            return None
        return response["result"]["sketch_id"]

    def create_test_lines(self, sketch_id: str, line_configs: list):
        """Helper to create multiple test lines"""
        lines = []
        for i, config in enumerate(line_configs):
            response = self.send_request('fusion.create_line', {
                "sketch_id": sketch_id,
                "start": config["start"],
                "end": config["end"]
            })
            if 'error' in response:
                return None
            lines.append(response["result"]["line_id"])
        return lines

    def test_basic_angular_dimension(self):
        """Test basic angular dimension functionality"""
        print("\n📐 Testing Basic Angular Dimension...")
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("basic_angular_dimension", False, {"error": "Failed to create sketch"})
            return False
            
        # Create two lines at 45 degrees
        lines = self.create_test_lines(sketch_id, [
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 0}},  # Horizontal
            {"start": {"x": 0, "y": 0}, "end": {"x": 7.07, "y": 7.07}}  # 45 degrees
        ])
        
        if not lines or len(lines) < 2:
            self.log_test_result("basic_angular_dimension", False, {"error": "Failed to create test lines"})
            return False
            
        # Add angular dimension
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": lines[0],
            "line2_id": lines[1],
            "angle_value": math.pi / 4,  # 45 degrees
            "text_position": {"x": 5, "y": 2}
        })
        
        if 'error' in response:
            self.log_test_result("basic_angular_dimension", False, {"error": response['error']})
            return False
            
        result = response["result"]
        self.log_test_result("basic_angular_dimension", True, {
            "dimension_id": result.get("dimension_id"),
            "angle_value": math.pi / 4,
            "is_driving": result.get("is_driving")
        })
        return True

    def test_angular_dimension_with_parameter(self):
        """Test angular dimension with named parameter"""
        print("\n📐 Testing Angular Dimension with Parameter...")
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("angular_dimension_parameter", False, {"error": "Failed to create sketch"})
            return False
            
        lines = self.create_test_lines(sketch_id, [
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 0}},  # Horizontal
            {"start": {"x": 0, "y": 0}, "end": {"x": 0, "y": 10}}   # Vertical (90 degrees)
        ])
        
        if not lines or len(lines) < 2:
            self.log_test_result("angular_dimension_parameter", False, {"error": "Failed to create test lines"})
            return False
            
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": lines[0],
            "line2_id": lines[1],
            "angle_value": math.pi / 2,  # 90 degrees
            "parameter_name": "right_angle",
            "text_position": {"x": 3, "y": 3}
        })
        
        if 'error' in response:
            self.log_test_result("angular_dimension_parameter", False, {"error": response['error']})
            return False
            
        result = response["result"]
        success = result.get("parameter") == "right_angle"
        self.log_test_result("angular_dimension_parameter", success, {
            "dimension_id": result.get("dimension_id"),
            "parameter_name": result.get("parameter"),
            "parameter_created": success
        })
        return success

    def test_edge_case_small_angle(self):
        """Test very small angle (edge case)"""
        print("\n📐 Testing Small Angle Edge Case...")
        self.test_results["summary"]["edge_cases_tested"] += 1
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("small_angle_edge_case", False, {"error": "Failed to create sketch"})
            return False
            
        # Create lines with very small angle (1 degree)
        small_angle = math.pi / 180  # 1 degree in radians
        lines = self.create_test_lines(sketch_id, [
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 0}},  # Horizontal
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": math.tan(small_angle) * 10}}  # 1 degree
        ])
        
        if not lines or len(lines) < 2:
            self.log_test_result("small_angle_edge_case", False, {"error": "Failed to create test lines"})
            return False
            
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": lines[0],
            "line2_id": lines[1],
            "angle_value": small_angle,
            "text_position": {"x": 8, "y": 1}
        })
        
        success = 'error' not in response
        self.log_test_result("small_angle_edge_case", success, {
            "angle_degrees": 1,
            "angle_radians": small_angle,
            "handled_correctly": success,
            "error": response.get('error') if not success else None
        })
        return success

    def test_edge_case_large_angle(self):
        """Test large angle (edge case)"""
        print("\n📐 Testing Large Angle Edge Case...")
        self.test_results["summary"]["edge_cases_tested"] += 1
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("large_angle_edge_case", False, {"error": "Failed to create sketch"})
            return False
            
        # Create lines with large angle (170 degrees)
        large_angle = 170 * math.pi / 180  # 170 degrees in radians
        lines = self.create_test_lines(sketch_id, [
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 0}},  # Horizontal
            {"start": {"x": 0, "y": 0}, "end": {"x": -9.85, "y": 1.74}}  # ~170 degrees
        ])
        
        if not lines or len(lines) < 2:
            self.log_test_result("large_angle_edge_case", False, {"error": "Failed to create test lines"})
            return False
            
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": lines[0],
            "line2_id": lines[1],
            "angle_value": large_angle,
            "text_position": {"x": 0, "y": 5}
        })
        
        success = 'error' not in response
        self.log_test_result("large_angle_edge_case", success, {
            "angle_degrees": 170,
            "angle_radians": large_angle,
            "handled_correctly": success,
            "error": response.get('error') if not success else None
        })
        return success

    def test_error_handling_invalid_lines(self):
        """Test error handling with invalid line IDs"""
        print("\n📐 Testing Error Handling - Invalid Lines...")
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("error_handling_invalid_lines", False, {"error": "Failed to create sketch"})
            return False
            
        # Try with invalid line IDs
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": "invalid_line_1",
            "line2_id": "invalid_line_2",
            "angle_value": math.pi / 4,
            "text_position": {"x": 5, "y": 2}
        })
        
        # This should fail with a proper error message
        success = 'error' in response and "not found" in response['error'].lower()
        self.log_test_result("error_handling_invalid_lines", success, {
            "expected_error": True,
            "got_error": 'error' in response,
            "error_message": response.get('error'),
            "proper_error_handling": success
        })
        return success

    def test_error_handling_missing_params(self):
        """Test error handling with missing required parameters"""
        print("\n📐 Testing Error Handling - Missing Parameters...")
        
        # Try without required parameters
        response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": "test_sketch",
            "line1_id": "line1"
            # Missing line2_id and angle_value
        })
        
        success = 'error' in response and "required" in response['error'].lower()
        self.log_test_result("error_handling_missing_params", success, {
            "expected_error": True,
            "got_error": 'error' in response,
            "error_message": response.get('error'),
            "proper_validation": success
        })
        return success

    def test_text_position_variants(self):
        """Test different text position configurations"""
        print("\n📐 Testing Text Position Variants...")
        
        sketch_id = self.create_test_sketch()
        if not sketch_id:
            self.log_test_result("text_position_variants", False, {"error": "Failed to create sketch"})
            return False
            
        lines = self.create_test_lines(sketch_id, [
            {"start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 0}},
            {"start": {"x": 0, "y": 0}, "end": {"x": 5, "y": 8.66}}  # 60 degrees
        ])
        
        if not lines or len(lines) < 2:
            self.log_test_result("text_position_variants", False, {"error": "Failed to create test lines"})
            return False
            
        # Test different text positions
        positions = [
            {"x": 0, "y": 0},     # Origin
            {"x": 5, "y": 3},     # Middle
            {"x": -2, "y": -1},   # Negative coords
            {"x": 15, "y": 10}    # Far away
        ]
        
        all_success = True
        position_results = []
        
        for i, pos in enumerate(positions):
            response = self.send_request('fusion.add_angular_dimension', {
                "sketch_id": sketch_id,
                "line1_id": lines[0],
                "line2_id": lines[1],
                "angle_value": math.pi / 3,  # 60 degrees
                "text_position": pos
            })
            
            success = 'error' not in response
            if not success:
                all_success = False
                
            position_results.append({
                "position": pos,
                "success": success,
                "error": response.get('error') if not success else None
            })
            
        self.log_test_result("text_position_variants", all_success, {
            "positions_tested": len(positions),
            "all_successful": all_success,
            "results": position_results
        })
        return all_success

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Angular Dimension Tests")
        print("=" * 60)
        
        if not self.connect():
            print("❌ Cannot connect to MCP server")
            return False
            
        try:
            # Run all test scenarios
            self.test_basic_angular_dimension()
            self.test_angular_dimension_with_parameter()
            self.test_edge_case_small_angle()
            self.test_edge_case_large_angle()
            self.test_error_handling_invalid_lines()
            self.test_error_handling_missing_params()
            self.test_text_position_variants()
            
            # Print comprehensive summary
            print("\n📊 COMPREHENSIVE TEST SUMMARY")
            print("=" * 40)
            summary = self.test_results["summary"]
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Passed: {summary['passed']}")
            print(f"Failed: {summary['failed']}")
            print(f"Edge Cases Tested: {summary['edge_cases_tested']}")
            print(f"Success Rate: {(summary['passed']/summary['total_tests']*100):.1f}%")
            
            overall_success = summary['failed'] == 0
            print(f"\n{'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ Test suite failed with exception: {e}")
            return False
            
        finally:
            self.save_results()
            if self.socket:
                self.socket.close()

    def save_results(self):
        """Save test results to file"""
        filename = f"test/angular_dimension_comprehensive_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"📄 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    tester = ComprehensiveAngularDimensionTester()
    success = tester.run_comprehensive_tests()
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
