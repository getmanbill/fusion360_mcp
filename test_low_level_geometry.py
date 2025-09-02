"""
Test Script: Low-Level Geometry Creation
Tests the new low-level endpoints that match the Fusion 360 API patterns more closely.
Based on the example provided, this demonstrates building geometries at a granular level.
"""
import socket
import json
import time

class FusionMCPClient:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the MCP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
    def send_request(self, method, params=None):
        """Send a request and receive response"""
        if params is None:
            params = {}
            
        request = {
            "method": method,
            "params": params,
            "id": 1
        }
        
        request_json = json.dumps(request) + '\n'
        self.socket.send(request_json.encode('utf-8'))
        
        response = self.socket.recv(4096).decode('utf-8')
        return json.loads(response)
        
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()

def test_low_level_geometry_creation():
    """Test the low-level geometry creation approach"""
    client = FusionMCPClient()
    
    try:
        print("🔗 Connecting to Fusion MCP server...")
        client.connect()
        print("✅ Connected successfully!")
        
        # Step 1: Create a new document (optional, but good practice)
        print("\n📄 Creating new document...")
        result = client.send_request('fusion.new_document')
        if 'error' in result:
            print(f"❌ Failed to create document: {result['error']}")
            return
        print("✅ Document created successfully!")
        
        # Step 2: Create a sketch on YZ plane (like the example)
        print("\n📐 Creating sketch on YZ plane...")
        result = client.send_request('fusion.create_sketch', {
            'plane_reference': 'YZ'  # Matches rootComp.yZConstructionPlane
        })
        if 'error' in result:
            print(f"❌ Failed to create sketch: {result['error']}")
            return
        
        sketch_id = result['result']['sketch_id']
        sketch_name = result['result']['sketch_name']
        print(f"✅ Sketch created: {sketch_name} (ID: {sketch_id})")
        
        # Step 3: Get initial revision ID (like print(sketch1.revisionId))
        print("\n🔍 Getting initial sketch revision ID...")
        result = client.send_request('fusion.get_sketch_revision_id', {
            'sketch_id': sketch_id
        })
        if 'error' in result:
            print(f"❌ Failed to get revision ID: {result['error']}")
            return
        
        initial_revision = result['result']['revision_id']
        print(f"✅ Initial revision ID: {initial_revision}")
        
        # Step 4: Create ObjectCollection (like ObjectCollection.create())
        print("\n📦 Creating ObjectCollection...")
        result = client.send_request('fusion.create_object_collection')
        if 'error' in result:
            print(f"❌ Failed to create ObjectCollection: {result['error']}")
            return
        
        collection_id = result['result']['collection_id']
        print(f"✅ ObjectCollection created: {collection_id}")
        
        # Step 5: Create individual Point3D objects (like Point3D.create())
        print("\n📍 Creating Point3D objects...")
        spline_points = [
            {'x': -5, 'y': 0, 'z': 0},
            {'x': 5, 'y': 1, 'z': 0},
            {'x': 6, 'y': 4, 'z': 3},
            {'x': 7, 'y': 6, 'z': 6},
            {'x': 2, 'y': 3, 'z': 0},
            {'x': 0, 'y': 1, 'z': 0}
        ]
        
        point_ids = []
        for i, point in enumerate(spline_points):
            result = client.send_request('fusion.create_point3d', point)
            if 'error' in result:
                print(f"❌ Failed to create Point3D {i}: {result['error']}")
                return
            
            point_id = result['result']['point_id']
            coords = result['result']['coordinates']
            point_ids.append(point_id)
            print(f"✅ Point {i}: {point_id} at ({coords['x']}, {coords['y']}, {coords['z']})")
        
        # Step 6: Create fitted spline using the collection approach
        print("\n🌊 Creating fitted spline from points...")
        result = client.send_request('fusion.create_fitted_spline_from_points', {
            'sketch_id': sketch_id,
            'points': spline_points
        })
        if 'error' in result:
            print(f"❌ Failed to create spline: {result['error']}")
            return
        
        spline_id = result['result']['entity_id']
        initial_rev = result['result']['initial_revision_id']
        final_rev = result['result']['final_revision_id']
        point_count = result['result']['point_count']
        collection_count = result['result']['collection_count']
        
        print(f"✅ Spline created: {spline_id}")
        print(f"   Points used: {point_count}")
        print(f"   Collection count: {collection_count}")
        print(f"   Revision: {initial_rev} → {final_rev}")
        
        # Step 7: Create rectangle using addTwoPointRectangle pattern
        print("\n📦 Creating rectangle with two points...")
        result = client.send_request('fusion.create_rectangle', {
            'sketch_id': sketch_id,
            'corner1': {'x': 0, 'y': 0},
            'corner2': {'x': 5.0, 'y': 5.0}
        })
        if 'error' in result:
            print(f"❌ Failed to create rectangle: {result['error']}")
            return
        
        rect_ids = result['result']['entity_ids']
        rect_initial_rev = result['result']['initial_revision_id']
        rect_final_rev = result['result']['final_revision_id']
        
        print(f"✅ Rectangle created with {len(rect_ids)} lines")
        print(f"   Line IDs: {rect_ids}")
        print(f"   Revision: {rect_initial_rev} → {rect_final_rev}")
        
        # Step 8: Get final sketch revision ID
        print("\n🔍 Getting final sketch revision ID...")
        result = client.send_request('fusion.get_sketch_revision_id', {
            'sketch_id': sketch_id
        })
        if 'error' in result:
            print(f"❌ Failed to get final revision ID: {result['error']}")
            return
        
        final_sketch_revision = result['result']['revision_id']
        print(f"✅ Final sketch revision ID: {final_sketch_revision}")
        
        # Step 9: Get detailed sketch info
        print("\n📊 Getting sketch information...")
        result = client.send_request('fusion.get_sketch_info', {
            'sketch_id': sketch_id
        })
        if 'error' in result:
            print(f"❌ Failed to get sketch info: {result['error']}")
            return
        
        sketch_info = result['result']
        entity_count = len(sketch_info.get('entities', []))
        constraint_count = len(sketch_info.get('constraints', []))
        
        print(f"✅ Sketch Info:")
        print(f"   Name: {sketch_info['name']}")
        print(f"   Entities: {entity_count}")
        print(f"   Constraints: {constraint_count}")
        print(f"   Plane: {sketch_info['reference_plane']}")
        
        print(f"\n🎉 Low-level geometry creation test completed successfully!")
        print(f"   Created: 1 sketch, 1 spline ({point_count} points), 1 rectangle (4 lines)")
        print(f"   Revisions tracked: {initial_revision} → {final_sketch_revision}")
        
    except Exception as e:
        print(f"💥 Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        client.close()
        print("🔌 Connection closed")

def test_individual_point_creation():
    """Test creating individual Point3D objects"""
    client = FusionMCPClient()
    
    try:
        print("\n🔗 Testing individual Point3D creation...")
        client.connect()
        
        test_points = [
            {'x': 0, 'y': 0, 'z': 0},
            {'x': 1.5, 'y': 2.7, 'z': 0},
            {'x': -3.14, 'y': 2.71, 'z': 1.41}
        ]
        
        for i, point in enumerate(test_points):
            result = client.send_request('fusion.create_point3d', point)
            if 'error' in result:
                print(f"❌ Point {i} failed: {result['error']}")
                continue
                
            coords = result['result']['coordinates']
            print(f"✅ Point {i}: ({coords['x']}, {coords['y']}, {coords['z']})")
        
    except Exception as e:
        print(f"💥 Point creation test failed: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Testing Low-Level Geometry Creation")
    print("=" * 50)
    
    # Test individual component creation
    test_individual_point_creation()
    
    # Small delay between tests
    time.sleep(1)
    
    # Test full workflow
    test_low_level_geometry_creation()
    
    print("\n✅ All tests completed!")
