"""
Ellipse Implementation Test
Tests the create_ellipse() method after implementation
Based on discovery findings from test_ellipse_api_discovery.py
"""
import socket
import json
import math

class EllipseImplementationTest:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        
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
            while True:
                chunk = self.socket.recv(8192)
                if not chunk:
                    break
                response_data += chunk
                try:
                    response_str = response_data.decode('utf-8')
                    if response_str.endswith('\n') or response_str.count('{') == response_str.count('}'):
                        break
                except UnicodeDecodeError:
                    continue
            
            response_str = response_data.decode('utf-8')
            response = json.loads(response_str)
            
            return response
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def close(self):
        if self.socket:
            self.socket.close()

def test_ellipse_implementation():
    """
    Test the implemented create_ellipse method
    """
    tester = EllipseImplementationTest()
    
    if not tester.connect():
        return
        
    try:
        print("🧪 ELLIPSE IMPLEMENTATION TEST")
        print("=" * 50)
        
        # Setup test environment
        print("\n📄 Creating test document...")
        result = tester.send_request('fusion.new_document', {
            'document_type': 'FusionDesignDocumentType'
        })
        
        if 'error' in result:
            print(f"❌ Document creation failed: {result['error']}")
            return
        
        print("✅ Document created successfully")
        
        print("\n📐 Creating test sketch...")
        result = tester.send_request('fusion.create_sketch', {
            'plane_reference': 'XY',
            'name': 'EllipseImplementationTest'
        })
        
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
            
        sketch_id = result.get('result', {}).get('sketch_id')
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Test cases
        test_cases = [
            {
                "name": "Basic Ellipse",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 10, "y": 10},
                    "major_axis": 20,
                    "minor_axis": 10
                },
                "description": "Standard ellipse at (10,10) with major=20, minor=10"
            },
            {
                "name": "Circle (Equal Axes)",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 50, "y": 10},
                    "major_axis": 15,
                    "minor_axis": 15
                },
                "description": "Circle using ellipse method (major=minor=15)"
            },
            {
                "name": "Rotated Ellipse",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 90, "y": 10},
                    "major_axis": 25,
                    "minor_axis": 8,
                    "rotation": math.pi/4  # 45 degrees
                },
                "description": "45-degree rotated ellipse"
            },
            {
                "name": "Construction Ellipse",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 10, "y": 50},
                    "major_axis": 12,
                    "minor_axis": 6,
                    "construction": True
                },
                "description": "Construction geometry ellipse"
            },
            {
                "name": "Small Ellipse",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 50, "y": 50},
                    "major_axis": 2,
                    "minor_axis": 1
                },
                "description": "Very small ellipse (edge case)"
            }
        ]
        
        successful_tests = []
        failed_tests = []
        
        print(f"\n🧪 Running {len(test_cases)} test cases...")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            
            result = tester.send_request('fusion.create_ellipse', test_case['params'])
            
            if 'error' in result:
                print(f"   ❌ FAILED: {result['error']}")
                failed_tests.append({
                    "test": test_case['name'],
                    "error": result['error']
                })
            else:
                entity_result = result.get('result', {})
                entity_id = entity_result.get('entity_id', 'unknown')
                entity_type = entity_result.get('entity_type', 'unknown')
                
                print(f"   ✅ SUCCESS: Created {entity_type}")
                print(f"      Entity ID: {entity_id[:25]}...")
                
                # Validate returned data
                if 'center_point_id' in entity_result:
                    print(f"      Center Point ID: {entity_result['center_point_id'][:25]}...")
                
                if 'major_axis' in entity_result:
                    print(f"      Major Axis: {entity_result['major_axis']}")
                
                if 'minor_axis' in entity_result:
                    print(f"      Minor Axis: {entity_result['minor_axis']}")
                
                successful_tests.append({
                    "test": test_case['name'],
                    "entity_id": entity_id,
                    "result": entity_result
                })
        
        # Error case testing
        print(f"\n🚨 Testing Error Cases...")
        print("-" * 50)
        
        error_cases = [
            {
                "name": "Invalid Sketch ID",
                "params": {
                    "sketch_id": "invalid_sketch_id",
                    "center": {"x": 0, "y": 0},
                    "major_axis": 10,
                    "minor_axis": 5
                },
                "expected_error": "Sketch not found"
            },
            {
                "name": "Missing Center",
                "params": {
                    "sketch_id": sketch_id,
                    "major_axis": 10,
                    "minor_axis": 5
                },
                "expected_error": "center is required"
            },
            {
                "name": "Negative Major Axis",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 0, "y": 0},
                    "major_axis": -10,
                    "minor_axis": 5
                },
                "expected_error": "major_axis must be positive"
            },
            {
                "name": "Minor > Major (Invalid)",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 0, "y": 0},
                    "major_axis": 5,
                    "minor_axis": 10
                },
                "expected_error": "major_axis must be >= minor_axis"
            }
        ]
        
        for i, error_case in enumerate(error_cases, 1):
            print(f"\nError Test {i}: {error_case['name']}")
            
            result = tester.send_request('fusion.create_ellipse', error_case['params'])
            
            if 'error' in result:
                print(f"   ✅ CORRECTLY FAILED: {result['error']}")
                if error_case['expected_error'].lower() in result['error'].lower():
                    print(f"   ✅ Error message matches expectation")
                else:
                    print(f"   ⚠️  Unexpected error message (expected: {error_case['expected_error']})")
            else:
                print(f"   ❌ UNEXPECTEDLY SUCCEEDED: Should have failed")
        
        # Summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Successful tests: {len(successful_tests)}/{len(test_cases)}")
        print(f"Failed tests: {len(failed_tests)}/{len(test_cases)}")
        
        if successful_tests:
            print(f"\n✅ Successful Tests:")
            for test in successful_tests:
                print(f"   - {test['test']}")
        
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['error']}")
        
        # Get final sketch info
        result = tester.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
        if 'error' not in result:
            sketch_info = result.get('result', {})
            entity_count = sketch_info.get('entity_count', 0)
            print(f"\n📐 Final sketch contains {entity_count} entities")
            
        success_rate = len(successful_tests) / len(test_cases) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 IMPLEMENTATION TEST PASSED!")
        else:
            print("🔧 IMPLEMENTATION NEEDS WORK")
            
    finally:
        tester.close()

if __name__ == "__main__":
    test_ellipse_implementation()
