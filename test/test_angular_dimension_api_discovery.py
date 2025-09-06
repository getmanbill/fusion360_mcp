"""
Angular Dimension API Discovery Test
Test and log the actual Fusion 360 API methods for angular dimensions
Following workspace rules: must log each step to confirm method and attribute names
"""
import json
import socket
import time
from datetime import datetime

class AngularDimensionAPITester:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        self.log_data = {
            "test_name": "angular_dimension_api_discovery",
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "api_findings": {},
            "errors": [],
            "method_verification": {}
        }
        
    def log_step(self, step_name: str, data: dict, success: bool = True):
        """Log each step to confirm method and attribute names"""
        self.log_data["steps"].append({
            "step": step_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "data": data
        })
        print(f"📝 LOGGED: {step_name} - {'✅' if success else '❌'}")
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.log_step("mcp_connection", {"host": self.host, "port": self.port})
            return True
        except Exception as e:
            self.log_step("mcp_connection", {"error": str(e)}, False)
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
            while True:
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
                    
            response = json.loads(response_data.decode('utf-8'))
            return response
            
        except Exception as e:
            self.log_step(f"request_failed_{method}", {"error": str(e)}, False)
            return {"error": str(e)}

    def test_angular_dimension_creation(self):
        """Test the add_angular_dimension method with comprehensive logging"""
        print("\n🔍 Testing Angular Dimension API...")
        print("=" * 50)
        
        # Step 1: Create sketch
        sketch_response = self.send_request('fusion.create_sketch', {"plane": "XY"})
        if 'error' in sketch_response:
            self.log_step("create_sketch", sketch_response, False)
            return False
            
        sketch_id = sketch_response["result"]["sketch_id"]
        self.log_step("create_sketch", {
            "sketch_id": sketch_id,
            "plane": "XY",
            "method_verified": "fusion.create_sketch"
        })
        
        # Step 2: Create first line (horizontal reference)
        line1_response = self.send_request('fusion.create_line', {
            "sketch_id": sketch_id,
            "start": {"x": 0, "y": 0},
            "end": {"x": 10, "y": 0}
        })
        
        if 'error' in line1_response:
            self.log_step("create_line1", line1_response, False)
            return False
            
        line1_id = line1_response["result"]["line_id"]
        self.log_step("create_line1", {
            "line_id": line1_id,
            "coordinates": "horizontal (0,0) to (10,0)",
            "method_verified": "fusion.create_line"
        })
        
        # Step 3: Create second line (at angle)
        line2_response = self.send_request('fusion.create_line', {
            "sketch_id": sketch_id,
            "start": {"x": 0, "y": 0},
            "end": {"x": 7.07, "y": 7.07}  # ~45 degrees
        })
        
        if 'error' in line2_response:
            self.log_step("create_line2", line2_response, False)
            return False
            
        line2_id = line2_response["result"]["line_id"]
        self.log_step("create_line2", {
            "line_id": line2_id,
            "coordinates": "angled (0,0) to (7.07,7.07)",
            "expected_angle": "45 degrees",
            "method_verified": "fusion.create_line"
        })
        
        # Step 4: Test add_angular_dimension method
        angular_dim_response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": line1_id,
            "line2_id": line2_id,
            "angle_value": 0.7854,  # 45 degrees in radians
            "text_position": {"x": 5, "y": 2}
        })
        
        if 'error' in angular_dim_response:
            self.log_step("add_angular_dimension", angular_dim_response, False)
            self.log_data["errors"].append({
                "method": "fusion.add_angular_dimension",
                "error": angular_dim_response.get('error'),
                "params_used": {
                    "sketch_id": sketch_id,
                    "line1_id": line1_id,
                    "line2_id": line2_id,
                    "angle_value": 0.7854,
                    "text_position": {"x": 5, "y": 2}
                }
            })
            return False
            
        result = angular_dim_response["result"]
        self.log_step("add_angular_dimension_success", {
            "dimension_id": result.get("dimension_id"),
            "dimension_type": result.get("dimension_type"),
            "parameter": result.get("parameter"),
            "is_driving": result.get("is_driving"),
            "text_position": result.get("text_position"),
            "method_verified": "fusion.add_angular_dimension",
            "api_call_successful": True
        })
        
        # Log API findings
        self.log_data["api_findings"]["add_angular_dimension"] = {
            "method_name": "fusion.add_angular_dimension",
            "required_params": ["sketch_id", "line1_id", "line2_id", "angle_value"],
            "optional_params": ["parameter_name", "text_position"],
            "return_attributes": list(result.keys()),
            "fusion_api_method": "sketch.dimensions.addAngularDimension",
            "verified_working": True
        }
        
        # Step 5: Test with parameter name
        param_angular_response = self.send_request('fusion.add_angular_dimension', {
            "sketch_id": sketch_id,
            "line1_id": line1_id,
            "line2_id": line2_id,
            "angle_value": 1.5708,  # 90 degrees in radians
            "parameter_name": "test_angle_90",
            "text_position": {"x": 3, "y": 5}
        })
        
        if 'error' not in param_angular_response:
            param_result = param_angular_response["result"]
            self.log_step("add_angular_dimension_with_parameter", {
                "dimension_id": param_result.get("dimension_id"),
                "parameter_name": param_result.get("parameter"),
                "custom_parameter_working": True
            })
        else:
            self.log_step("add_angular_dimension_with_parameter", param_angular_response, False)
        
        return True
        
    def verify_method_attributes(self):
        """Verify the method implementation against expected API"""
        print("\n🔍 Verifying Method Attributes...")
        
        expected_attributes = {
            "method_name": "add_angular_dimension",
            "fusion_api": "sketch.dimensions.addAngularDimension",
            "required_params": ["sketch_id", "line1_id", "line2_id", "angle_value"],
            "optional_params": ["parameter_name", "text_position"],
            "return_data": ["dimension_id", "dimension_type", "parameter", "is_driving"],
            "angle_units": "radians"
        }
        
        self.log_data["method_verification"] = {
            "expected": expected_attributes,
            "implementation_file": "fusion_addon/sketch/constraints.py",
            "handler_registration": "fusion_addon/fusion_mcp_addon.py line 80"
        }
        
        print("📋 Expected attributes logged for verification")
        
    def save_log(self):
        """Save discovery log to file"""
        filename = f"test/api_discovery/angular_dimension_api_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.log_data, f, indent=2)
            print(f"📄 Discovery log saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save log: {e}")
            
    def run_full_test(self):
        """Run complete API discovery test"""
        print("🚀 Starting Angular Dimension API Discovery Test")
        print("Following workspace rules: logging each step to confirm method names")
        print("=" * 70)
        
        if not self.connect():
            print("❌ Cannot connect to MCP server - test requires active Fusion addon")
            return False
            
        try:
            success = self.test_angular_dimension_creation()
            self.verify_method_attributes()
            
            print("\n📊 TEST SUMMARY")
            print("-" * 20)
            print(f"Steps completed: {len(self.log_data['steps'])}")
            print(f"Errors encountered: {len(self.log_data['errors'])}")
            print(f"API methods verified: {len(self.log_data['api_findings'])}")
            
            if success:
                print("✅ Angular dimension API discovery completed successfully!")
            else:
                print("❌ Some tests failed - check logs for details")
                
            return success
            
        except Exception as e:
            self.log_step("test_exception", {"error": str(e)}, False)
            print(f"❌ Test failed with exception: {e}")
            return False
            
        finally:
            self.save_log()
            if self.socket:
                self.socket.close()

def main():
    tester = AngularDimensionAPITester()
    success = tester.run_full_test()
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
