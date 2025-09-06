"""
Debug Arc API Discovery
Discover actual available arc creation methods and attributes in Fusion API
"""
import socket
import json

class ArcAPIDiscovery:
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

def discover_arc_api():
    """Discover actual arc API by testing different approaches"""
    tester = ArcAPIDiscovery()
    
    if not tester.connect():
        return
        
    try:
        print("🔍 ARC API DISCOVERY - STEP BY STEP DEBUG")
        print("=" * 60)
        
        # Create document and sketch
        print("\n📄 Step 1: Creating test document...")
        result = tester.send_request('fusion.new_document', {'document_type': 'FusionDesignDocumentType'})
        if 'error' in result:
            print(f"❌ Document creation failed: {result['error']}")
            return
        print("✅ Document created")
        
        print("\n📐 Step 2: Creating test sketch...")
        result = tester.send_request('fusion.create_sketch', {'plane_reference': 'XY', 'name': 'ArcDebugSketch'})
        if 'error' in result:
            print(f"❌ Sketch creation failed: {result['error']}")
            return
        sketch_id = result.get('result', {}).get('sketch_id')
        print(f"✅ Sketch created: {sketch_id[:20]}...")
        
        # Step 3: Test the current broken arc method with detailed logging
        print("\n🐛 Step 3: Testing current broken arc method...")
        print("   Current parameters:")
        arc_params = {
            "sketch_id": sketch_id,
            "center": {"x": 10, "y": 10},
            "radius": 5,
            "start_angle": 0,
            "end_angle": 1.57  # 90 degrees
        }
        
        for key, value in arc_params.items():
            print(f"     {key}: {value}")
        
        result = tester.send_request('fusion.create_arc', arc_params)
        
        if 'error' in result:
            error = result['error']
            print(f"   ❌ FAILED with error: {error}")
            
            # Parse the error for clues
            if "InternalValidationError" in error:
                print("   🔍 Analysis: InternalValidationError suggests parameter/API mismatch")
            if "getAcGePoint3D" in error:
                print("   🔍 Analysis: Point3D conversion issue - wrong parameter format")
            if "centerPoint" in error:
                print("   🔍 Analysis: Issue with center point parameter")
                
        else:
            print("   ✅ Unexpectedly worked! Result:")
            print(f"     {result.get('result', {})}")
        
        # Step 4: Try alternative arc creation approaches
        print(f"\n🧪 Step 4: Testing alternative arc creation methods...")
        
        # Test if we can create working geometry to compare
        print("\n   4a. Creating working circle for comparison...")
        result = tester.send_request('fusion.create_circle', {
            "sketch_id": sketch_id,
            "center": {"x": 30, "y": 10},
            "radius": 5
        })
        
        if 'error' not in result:
            print("   ✅ Circle creation works fine - parameter format is correct")
            circle_result = result.get('result', {})
            print(f"     Circle entity_id: {circle_result.get('entity_id', 'unknown')[:20]}...")
            print(f"     Circle center_point_id: {circle_result.get('center_point_id', 'unknown')[:20]}...")
        else:
            print(f"   ❌ Even circle failed: {result['error']}")
        
        # Test working line for comparison
        print("\n   4b. Creating working line for comparison...")
        result = tester.send_request('fusion.create_line', {
            "sketch_id": sketch_id,
            "start_point": {"x": 50, "y": 10},
            "end_point": {"x": 60, "y": 20}
        })
        
        if 'error' not in result:
            print("   ✅ Line creation works fine")
            line_result = result.get('result', {})
            print(f"     Line entity_id: {line_result.get('entity_id', 'unknown')[:20]}...")
        else:
            print(f"   ❌ Even line failed: {result['error']}")
        
        # Step 5: Examine what we have so far
        print(f"\n📊 Step 5: Examining current sketch state...")
        result = tester.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
        
        if 'error' not in result:
            sketch_info = result.get('result', {})
            entities = sketch_info.get('entities', [])
            
            print(f"   Total entities: {len(entities)}")
            
            # Look for any arc-related entities or clues
            entity_types = {}
            for entity in entities:
                etype = entity.get('type', 'unknown')
                entity_types[etype] = entity_types.get(etype, 0) + 1
                
                # Log any arc-related types
                if 'arc' in etype.lower() or 'curve' in etype.lower():
                    print(f"   🎯 Found curve-related entity: {etype}")
                    print(f"      Entity details: {entity}")
            
            print(f"   Entity types present:")
            for etype, count in entity_types.items():
                print(f"     {etype}: {count}")
        else:
            print(f"   ❌ Sketch info failed: {result['error']}")
        
        # Step 6: Try to discover arc methods by looking at implementation
        print(f"\n🔍 Step 6: Analysis and next steps...")
        
        print("   Based on working methods (circle, line), the parameter format is correct.")
        print("   The error suggests the arc implementation has a bug in Point3D handling.")
        print("   Need to examine the actual arc creation code in geometry.py")
        
        # Step 7: Test various parameter combinations that might work
        print(f"\n🧪 Step 7: Testing arc parameter variations...")
        
        arc_variations = [
            {
                "name": "Simple arc with integer coordinates",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 70, "y": 10},
                    "radius": 5,
                    "start_angle": 0.0,
                    "end_angle": 1.57
                }
            },
            {
                "name": "Arc with different angle range",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 70, "y": 30},
                    "radius": 3,
                    "start_angle": 0.5,
                    "end_angle": 3.14
                }
            }
        ]
        
        working_arc_params = None
        
        for variation in arc_variations:
            print(f"\n   Testing: {variation['name']}")
            result = tester.send_request('fusion.create_arc', variation['params'])
            
            if 'error' in result:
                print(f"     ❌ Failed: {result['error'][:100]}...")
            else:
                print(f"     ✅ SUCCESS! Found working parameters!")
                working_arc_params = variation['params']
                arc_result = result.get('result', {})
                print(f"       Arc entity_id: {arc_result.get('entity_id', 'unknown')[:20]}...")
                break
        
        # Final analysis
        print(f"\n📋 FINAL ANALYSIS")
        print("=" * 60)
        
        if working_arc_params:
            print("✅ Found working arc parameters!")
            print("   Working params:", working_arc_params)
        else:
            print("❌ All arc attempts failed.")
            print("   🔍 Next step: Examine geometry.py arc implementation")
            print("   🔍 Look for Point3D creation differences vs working methods")
            
    finally:
        tester.close()
        print(f"\n🔌 Connection closed")

if __name__ == "__main__":
    discover_arc_api()
