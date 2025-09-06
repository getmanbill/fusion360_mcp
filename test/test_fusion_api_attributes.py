"""
Fusion API Attribute Discovery Test
Log actual available attributes and methods on Fusion API objects
"""
import socket
import json

class FusionAPIAttributeTester:
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

def discover_fusion_api_attributes():
    """Discover actual available attributes on Fusion API objects"""
    tester = FusionAPIAttributeTester()
    
    if not tester.connect():
        return
        
    try:
        print("🔍 FUSION API ATTRIBUTE DISCOVERY")
        print("=" * 60)
        
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
            'name': 'AttributeDiscoverySketch'
        })
        
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
            
        sketch_id = result.get('result', {}).get('sketch_id')
        if not sketch_id:
            print("❌ No sketch_id returned")
            return
            
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Add a custom MCP method to inspect API objects
        print(f"\n🔬 Creating API inspection methods...")
        
        # First, let's see what's in the actual implementation by requesting a comprehensive test
        test_methods = [
            # Try getting detailed sketch curves info
            {
                "method": "fusion.inspect_sketch_curves",
                "params": {"sketch_id": sketch_id},
                "description": "Inspect sketch curves API"
            },
            # Try getting sketch info to see available entity types
            {
                "method": "fusion.get_sketch_info", 
                "params": {"sketch_id": sketch_id},
                "description": "Get complete sketch API info"
            }
        ]
        
        working_info = {}
        
        for test in test_methods:
            print(f"\n🧪 Testing: {test['description']}")
            print(f"   Method: {test['method']}")
            
            result = tester.send_request(test['method'], test['params'])
            
            if 'error' in result:
                error = result['error']
                if "Unknown method" in error:
                    print(f"   ❌ Method not available: {error}")
                else:
                    print(f"   ⚠️  Method exists but failed: {error}")
            else:
                print(f"   ✅ SUCCESS: Got API info!")
                working_info[test['method']] = result.get('result', {})
                
                # Print useful details
                if test['method'] == 'fusion.get_sketch_info':
                    sketch_info = result.get('result', {})
                    print(f"      Sketch name: {sketch_info.get('name', 'unknown')}")
                    print(f"      Entity count: {len(sketch_info.get('entities', []))}")
                    print(f"      Has sketchCurves: {'sketch_curves' in sketch_info}")
                    if 'sketch_curves' in sketch_info:
                        curves = sketch_info['sketch_curves']
                        print(f"      Available curve types: {list(curves.keys())}")
        
        # Now let's create some geometry and inspect what we get back
        print(f"\n🧪 Creating geometry to inspect available API...")
        
        geometry_tests = [
            {
                "method": "fusion.create_line",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 10, "y": 10}
                },
                "description": "Line API"
            },
            {
                "method": "fusion.create_circle", 
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 20, "y": 20},
                    "radius": 5
                },
                "description": "Circle API"
            },
            {
                "method": "fusion.create_arc",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 30, "y": 30},
                    "radius": 8,
                    "start_angle": 0,
                    "end_angle": 1.57  # 90 degrees
                },
                "description": "Arc API"
            }
        ]
        
        created_entities = {}
        
        for test in geometry_tests:
            print(f"\n🧪 Creating: {test['description']}")
            
            result = tester.send_request(test['method'], test['params'])
            
            if 'error' in result:
                print(f"   ❌ Failed: {result['error']}")
            else:
                print(f"   ✅ Created successfully!")
                entity_info = result.get('result', {})
                entity_id = entity_info.get('entity_id', 'unknown')
                entity_type = entity_info.get('entity_type', 'unknown')
                
                print(f"      Entity ID: {entity_id[:20]}...")
                print(f"      Entity Type: {entity_type}")
                
                # Log all returned attributes
                print(f"      Returned attributes:")
                for key, value in entity_info.items():
                    if key not in ['entity_id']:  # Skip the long ID
                        print(f"        {key}: {value}")
                
                created_entities[entity_type] = entity_info
        
        # Get updated sketch info to see all entities
        print(f"\n📊 FINAL SKETCH INSPECTION")
        print("-" * 50)
        
        result = tester.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
        if 'error' not in result:
            sketch_info = result.get('result', {})
            entities = sketch_info.get('entities', [])
            
            print(f"Total entities created: {len(entities)}")
            
            # Group by entity type
            entity_types = {}
            for entity in entities:
                etype = entity.get('type', 'unknown')
                if etype not in entity_types:
                    entity_types[etype] = []
                entity_types[etype].append(entity)
            
            print(f"\nEntity types found:")
            for etype, entities_list in entity_types.items():
                print(f"  {etype}: {len(entities_list)} instances")
                
                # Show available attributes for first instance
                if entities_list:
                    first_entity = entities_list[0]
                    print(f"    Available attributes:")
                    for attr_name, attr_value in first_entity.items():
                        if attr_name != 'id':  # Skip long IDs
                            attr_type = type(attr_value).__name__
                            print(f"      {attr_name} ({attr_type}): {str(attr_value)[:50]}...")
            
            # Check if sketch has more API surface area
            print(f"\nSketch-level attributes:")
            for key, value in sketch_info.items():
                if key not in ['entities', 'sketch_id']:
                    print(f"  {key}: {str(value)[:100]}...")
                    
        # Summary of what we learned
        print(f"\n📋 API DISCOVERY SUMMARY")
        print("=" * 60)
        print("Working geometry methods:")
        for entity_type, info in created_entities.items():
            print(f"  ✅ fusion.create_{entity_type}")
            
        print(f"\nNext steps for expanding API:")
        print("  1. Look for more sketch curve types in adsk.fusion.SketchCurves")
        print("  2. Check for additional creation methods on existing curve types")
        print("  3. Explore constraint and dimension APIs")
        print("  4. Test pattern and mirror operations")
            
    finally:
        tester.close()
        print(f"\n🔌 Connection closed")

if __name__ == "__main__":
    discover_fusion_api_attributes()
