"""
Test what's actually available in SketchCurves API
"""
import socket
import json

class SketchCurvesDiscovery:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
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

def test_existing_methods():
    """Test the methods we already implemented to see what actually works"""
    tester = SketchCurvesDiscovery()
    
    if not tester.connect():
        return
        
    try:
        print("🔍 TESTING EXISTING IMPLEMENTED METHODS")
        print("=" * 60)
        
        # Create document and sketch
        result = tester.send_request('fusion.new_document', {'document_type': 'FusionDesignDocumentType'})
        if 'error' in result:
            print(f"❌ Document creation failed: {result['error']}")
            return
        print("✅ Document created")
        
        result = tester.send_request('fusion.create_sketch', {'plane_reference': 'XY', 'name': 'TestSketch'})
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
        sketch_id = result.get('result', {}).get('sketch_id')
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Test methods we know exist in geometry.py
        tests = [
            {
                "method": "fusion.create_polygon",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 0, "y": 0},
                    "sides": 6,
                    "radius": 10
                },
                "description": "Hexagon"
            },
            {
                "method": "fusion.create_spline", 
                "params": {
                    "sketch_id": sketch_id,
                    "points": [
                        {"x": 20, "y": 20},
                        {"x": 30, "y": 25},
                        {"x": 40, "y": 20},
                        {"x": 50, "y": 30}
                    ]
                },
                "description": "Spline curve"
            },
            {
                "method": "fusion.create_fitted_spline_from_points",
                "params": {
                    "sketch_id": sketch_id,
                    "points": [
                        {"x": 60, "y": 20},
                        {"x": 70, "y": 25},
                        {"x": 80, "y": 20}
                    ]
                },
                "description": "Fitted spline"
            },
            {
                "method": "fusion.add_two_point_rectangle",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 90, "y": 20},
                    "end_point": {"x": 100, "y": 30}
                },
                "description": "Two-point rectangle"
            }
        ]
        
        working_methods = []
        failed_methods = []
        
        for test in tests:
            print(f"\n🧪 Testing: {test['description']}")
            print(f"   Method: {test['method']}")
            
            result = tester.send_request(test['method'], test['params'])
            
            if 'error' in result:
                error = result['error']
                print(f"   ❌ FAILED: {error}")
                failed_methods.append({
                    "method": test['method'],
                    "error": error,
                    "description": test['description']
                })
            else:
                print(f"   ✅ SUCCESS!")
                entity_info = result.get('result', {})
                
                # Log what we got back
                if 'entity_id' in entity_info:
                    print(f"      Single entity: {entity_info.get('entity_type', 'unknown')}")
                elif 'entity_ids' in entity_info:
                    print(f"      Multiple entities: {len(entity_info['entity_ids'])} of type {entity_info.get('entity_type', 'unknown')}")
                
                working_methods.append({
                    "method": test['method'],
                    "description": test['description'],
                    "result": entity_info
                })
        
        # Get final sketch state
        print(f"\n📊 FINAL SKETCH STATE")
        print("-" * 50)
        
        result = tester.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
        if 'error' not in result:
            sketch_info = result.get('result', {})
            entities = sketch_info.get('entities', [])
            
            print(f"Total entities: {len(entities)}")
            
            entity_types = {}
            for entity in entities:
                etype = entity.get('type', 'unknown')
                entity_types[etype] = entity_types.get(etype, 0) + 1
            
            for etype, count in entity_types.items():
                print(f"  {etype}: {count}")
        
        # Results summary
        print(f"\n📋 RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"✅ Working methods ({len(working_methods)}):")
        for method_info in working_methods:
            print(f"   {method_info['method']} - {method_info['description']}")
        
        print(f"\n❌ Failed methods ({len(failed_methods)}):")
        for method_info in failed_methods:
            print(f"   {method_info['method']} - {method_info['description']}")
            print(f"      Error: {method_info['error'][:100]}...")
            
        # Analysis
        print(f"\n🔬 ANALYSIS")
        print("-" * 30)
        if len(working_methods) > 0:
            print(f"✅ We have {len(working_methods)} additional working geometry methods!")
            print("   These should be documented and prioritized.")
        else:
            print("❌ No additional methods working - need to focus on basics.")
            
        if len(failed_methods) > 0:
            print(f"⚠️  {len(failed_methods)} methods need debugging:")
            for method_info in failed_methods:
                if "Unknown method" in method_info['error']:
                    print(f"   - {method_info['method']}: Not registered in MCP")
                else:
                    print(f"   - {method_info['method']}: Implementation bug")
            
    finally:
        tester.close()
        print(f"\n🔌 Connection closed")

if __name__ == "__main__":
    test_existing_methods()
