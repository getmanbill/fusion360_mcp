"""
Slot Implementation Test
Tests the create_slot() method after implementation
Based on discovery findings from test_slot_api_discovery.py
"""
import socket
import json
import math

class SlotImplementationTest:
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

def test_slot_implementation():
    """
    Test the implemented create_slot method
    """
    tester = SlotImplementationTest()
    
    if not tester.connect():
        return
        
    try:
        print("🧪 SLOT IMPLEMENTATION TEST")
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
            'name': 'SlotImplementationTest'
        })
        
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
            
        sketch_id = result.get('result', {}).get('sketch_id')
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Test cases based on discovery test requirements
        test_cases = [
            {
                "name": "Horizontal Slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 20, "y": 0},
                    "width": 5
                },
                "description": "Horizontal slot from (0,0) to (20,0) with width 5"
            },
            {
                "name": "Vertical Slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 30, "y": 0},
                    "end_point": {"x": 30, "y": 20},
                    "width": 3
                },
                "description": "Vertical slot from (30,0) to (30,20) with width 3"
            },
            {
                "name": "Diagonal Slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 50, "y": 0},
                    "end_point": {"x": 60, "y": 10},
                    "width": 4
                },
                "description": "Diagonal slot from (50,0) to (60,10) with width 4"
            },
            {
                "name": "Construction Slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 30},
                    "end_point": {"x": 15, "y": 30},
                    "width": 6,
                    "construction": True
                },
                "description": "Construction geometry slot"
            },
            {
                "name": "Small Slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 70, "y": 0},
                    "end_point": {"x": 72, "y": 0},
                    "width": 1
                },
                "description": "Very small slot (edge case)"
            }
        ]
        
        successful_tests = []
        failed_tests = []
        
        print(f"\n🧪 Running {len(test_cases)} test cases...")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            
            result = tester.send_request('fusion.create_slot', test_case['params'])
            
            if 'error' in result:
                print(f"   ❌ FAILED: {result['error']}")
                failed_tests.append({
                    "test": test_case['name'],
                    "error": result['error']
                })
            else:
                entity_result = result.get('result', {})
                entity_ids = entity_result.get('entity_ids', [])
                entity_type = entity_result.get('entity_type', 'unknown')
                slot_length = entity_result.get('slot_length', 'unknown')
                slot_width = entity_result.get('slot_width', 'unknown')
                component_count = entity_result.get('component_count', 0)
                
                print(f"   ✅ SUCCESS: Created {entity_type}")
                print(f"      Entity Count: {component_count} components")
                print(f"      Slot Length: {slot_length}")
                print(f"      Slot Width: {slot_width}")
                
                # Validate composite geometry structure
                if component_count == 4:
                    print(f"      ✅ Correct component count (2 arcs + 2 lines)")
                    components = entity_result.get('components', {})
                    if all(components.get(key) for key in ['left_arc', 'right_arc', 'top_line', 'bottom_line']):
                        print(f"      ✅ All slot components created successfully")
                    else:
                        print(f"      ⚠️  Some slot components missing")
                else:
                    print(f"      ❌ Incorrect component count (expected 4, got {component_count})")
                
                successful_tests.append({
                    "test": test_case['name'],
                    "entity_ids": entity_ids,
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
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 10, "y": 0},
                    "width": 5
                },
                "expected_error": "Sketch not found"
            },
            {
                "name": "Missing Start Point",
                "params": {
                    "sketch_id": sketch_id,
                    "end_point": {"x": 10, "y": 0},
                    "width": 5
                },
                "expected_error": "start_point is required"
            },
            {
                "name": "Negative Width",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 10, "y": 0},
                    "width": -5
                },
                "expected_error": "width must be positive"
            },
            {
                "name": "Same Start/End Points",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 0, "y": 0},
                    "width": 5
                },
                "expected_error": "must be different"
            }
        ]
        
        for i, error_case in enumerate(error_cases, 1):
            print(f"\nError Test {i}: {error_case['name']}")
            
            result = tester.send_request('fusion.create_slot', error_case['params'])
            
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
            print("🎉 SLOT IMPLEMENTATION TEST PASSED!")
        else:
            print("🔧 SLOT IMPLEMENTATION NEEDS WORK")
            
    finally:
        tester.close()

if __name__ == "__main__":
    test_slot_implementation()
