"""
Sketch API Discovery Test
Test what sketch geometry methods are actually available in Fusion 360 API
"""
import socket
import json

class SketchAPITester:
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
            
            # Read complete response 
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

def discover_sketch_api():
    """Discover what sketch API methods are actually available"""
    tester = SketchAPITester()
    
    if not tester.connect():
        return
        
    try:
        print("🔍 SKETCH API DISCOVERY TEST")
        print("=" * 50)
        
        # Create new document first
        print("\n📄 Creating test document...")
        result = tester.send_request('fusion.new_document', {
            'document_type': 'FusionDesignDocumentType'
        })
        
        if 'error' in result:
            print(f"❌ Document creation failed: {result['error']}")
            return
        
        print("✅ Document created successfully")
        
        # Create test sketch
        print("\n📐 Creating test sketch...")
        result = tester.send_request('fusion.create_sketch', {
            'plane_reference': 'XY',
            'name': 'APIDiscoverySketch'
        })
        
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
            
        sketch_id = result.get('result', {}).get('sketch_id')
        if not sketch_id:
            print("❌ No sketch_id returned")
            return
            
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Test potential geometry methods by trying them
        print(f"\n🧪 Testing Available Geometry Methods")
        print("-" * 50)
        
        test_methods = [
            # Known working methods
            {
                "method": "fusion.create_line",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 10, "y": 10}
                },
                "description": "Basic line"
            },
            {
                "method": "fusion.create_circle", 
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 20, "y": 20},
                    "radius": 5
                },
                "description": "Basic circle"
            },
            {
                "method": "fusion.create_rectangle",
                "params": {
                    "sketch_id": sketch_id,
                    "corner1": {"x": 30, "y": 30},
                    "corner2": {"x": 40, "y": 40}
                },
                "description": "Basic rectangle"
            },
            # Test potential new methods
            {
                "method": "fusion.create_ellipse",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 50, "y": 50},
                    "major_axis": 10,
                    "minor_axis": 5
                },
                "description": "Ellipse (test if available)"
            },
            {
                "method": "fusion.create_slot",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 60, "y": 60},
                    "end_point": {"x": 70, "y": 60},
                    "width": 4
                },
                "description": "Slot (test if available)"
            },
            {
                "method": "fusion.create_construction_line",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 50},
                    "end_point": {"x": 100, "y": 50}
                },
                "description": "Construction line (test if available)"
            }
        ]
        
        working_methods = []
        unknown_methods = []
        
        for test in test_methods:
            print(f"\n🧪 Testing: {test['description']}")
            print(f"   Method: {test['method']}")
            
            result = tester.send_request(test['method'], test['params'])
            
            if 'error' in result:
                error = result['error']
                if "Unknown method" in error:
                    print(f"   ❌ NOT AVAILABLE: {error}")
                    unknown_methods.append(test['method'])
                else:
                    print(f"   ⚠️  METHOD EXISTS but failed: {error}")
                    working_methods.append(test['method'])
            else:
                print(f"   ✅ SUCCESS: Method works!")
                entity_id = result.get('result', {}).get('entity_id', 'unknown')
                print(f"      Created entity: {entity_id[:20]}...")
                working_methods.append(test['method'])
        
        # Summary
        print(f"\n📊 API DISCOVERY SUMMARY")
        print("=" * 50)
        print(f"Working methods ({len(working_methods)}):")
        for method in working_methods:
            print(f"   ✅ {method}")
            
        print(f"\nNot available methods ({len(unknown_methods)}):")
        for method in unknown_methods:
            print(f"   ❌ {method}")
            
        # Test available sketch curve types by exploring the API
        print(f"\n🔬 Advanced API Exploration")
        print("-" * 50)
        
        # Get detailed sketch info to see what's actually in there
        result = tester.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
        if 'error' not in result:
            sketch_info = result.get('result', {})
            entities = sketch_info.get('entities', [])
            print(f"   Created {len(entities)} entities successfully")
            for i, entity in enumerate(entities[:3]):  # Show first 3 entities
                entity_type = entity.get('type', 'unknown')
                entity_id = entity.get('id', 'unknown')
                print(f"   Entity {i+1}: {entity_type} (ID: {entity_id[:15]}...)")
        else:
            print(f"   ⚠️  Sketch info failed: {result['error']}")
            
    finally:
        tester.close()
        print(f"\n🔌 Connection closed")

if __name__ == "__main__":
    discover_sketch_api()
