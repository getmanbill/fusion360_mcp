"""
Test Script: Exact Match to Fusion 360 Example
Replicates the exact steps from the provided example script using MCP endpoints.

Original script flow:
1. app = adsk.core.Application.get()
2. ui = app.userInterface  
3. doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
4. product = app.activeProduct
5. design = adsk.fusion.Design.cast(product)
6. rootComp = design.rootComponent
7. sketches = rootComp.sketches
8. sketch1 = sketches.add(rootComp.yZConstructionPlane)
9. print(sketch1.revisionId)
10. points = adsk.core.ObjectCollection.create()
11. points.add(adsk.core.Point3D.create(-5, 0, 0)) ... (6 points)
12. spline = sketch1.sketchCurves.sketchFittedSplines.add(points)
13. print(sketch1.revisionId)
14. sketchLines = sketch1.sketchCurves.sketchLines
15. startPoint = adsk.core.Point3D.create(0, 0, 0)
16. endPoint = adsk.core.Point3D.create(5.0, 5.0, 0)
17. sketchLines.addTwoPointRectangle(startPoint, endPoint)
18. print(sketch1.revisionId)
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

def test_exact_example_workflow():
    """Test that replicates the exact example script workflow"""
    client = FusionMCPClient()
    
    try:
        print("🚀 EXACT EXAMPLE SCRIPT TEST")
        print("=" * 50)
        print("Replicating the exact Fusion 360 API example via MCP...")
        
        print("\n🔗 Step 1: Connecting to Fusion MCP server...")
        client.connect()
        print("✅ Connected successfully!")
        
        # Step 2: Create a document (like app.documents.add(DocumentTypes.FusionDesignDocumentType))
        print("\n📄 Step 2: Create document (app.documents.add)...")
        result = client.send_request('fusion.new_document', {
            'document_type': 'FusionDesignDocumentType'
        })
        
        print(f"\n🔍 DEBUG - Full result object:")
        print(f"   Type: {type(result)}")
        print(f"   All attributes: {dir(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"\n🔍 DEBUG - Dictionary keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ Failed to create document: {result['error']}")
            return
        
        if 'result' in result and isinstance(result['result'], dict):
            doc_result = result['result'] 
            if 'error' in doc_result:
                print(f"❌ Error in document result: {doc_result['error']}")
                return
            doc_info = doc_result
            
            print(f"\n🔍 DEBUG - doc_info object:")
            print(f"   Type: {type(doc_info)}")
            print(f"   Raw doc_info: {doc_info}")
            if isinstance(doc_info, dict):
                print(f"   Keys: {list(doc_info.keys())}")
                for key, value in doc_info.items():
                    print(f"   {key}: {value} (type: {type(value)})")
        else:
            print("❌ No valid 'result' key in response or result is not dict")
            return
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        # Use ALL .get() with safe defaults - NO assumptions about field names
        doc_name = doc_info.get('document_name', doc_info.get('name', 'UNKNOWN'))
        product_type = doc_info.get('product_type', 'UNKNOWN')
        design_info = doc_info.get('design_id', doc_info.get('design_type', 'UNKNOWN'))
        root_comp = doc_info.get('root_component_id', 'UNKNOWN')
        
        print(f"✅ Document info extracted:")
        print(f"   Name: {doc_name}")
        print(f"   Product type: {product_type}")
        print(f"   Design info: {design_info}")
        print(f"   Root component: {root_comp}")
        
        # Step 3: Get root component (like rootComp = design.rootComponent)
        print("\n🏗️ Step 3: Get root component (design.rootComponent)...")
        result = client.send_request('fusion.get_root_component')
        
        print(f"\n🔍 DEBUG - Root component result:")
        print(f"   Type: {type(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ Failed to get root component: {result['error']}")
            return
        
        if 'result' in result and isinstance(result['result'], dict):
            root_result = result['result']
            if 'error' in root_result:
                print(f"❌ Error in root component result: {root_result['error']}")
                return
            root_comp = root_result
        else:
            print("❌ Unexpected root component response structure")
            return
            
        # Safe field extraction - no assumptions
        comp_id = root_comp.get('root_component_id', root_comp.get('component_id', 'UNKNOWN'))
        design_type = root_comp.get('design_type', root_comp.get('design_name', 'UNKNOWN'))
        sketches_count = root_comp.get('sketches_count', 'UNKNOWN')
        features_count = root_comp.get('features_count', 'UNKNOWN')
        
        print(f"✅ Root component info:")
        print(f"   Component ID: {comp_id}")
        print(f"   Design type: {design_type}")
        print(f"   Sketches count: {sketches_count}")
        print(f"   Features count: {features_count}")
        
        # Step 4: Create sketch on YZ plane (like sketches.add(rootComp.yZConstructionPlane))
        print("\n📐 Step 4: Create sketch (sketches.add(yZConstructionPlane))...")
        result = client.send_request('fusion.create_sketch', {
            'plane_reference': 'YZ'
        })
        
        print(f"\n🔍 DEBUG - Sketch creation result:")
        print(f"   Type: {type(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ Failed to create sketch: {result['error']}")
            return
        
        if 'result' in result and isinstance(result['result'], dict):
            sketch_result = result['result']
            if 'error' in sketch_result:
                print(f"❌ Error in sketch result: {sketch_result['error']}")
                return
            sketch_info = sketch_result
        else:
            print("❌ Unexpected sketch response structure")
            return
            
        # Safe field extraction - try multiple possible field names
        sketch_id = sketch_info.get('sketch_id', sketch_info.get('id', sketch_info.get('entity_id', 'UNKNOWN')))
        sketch_name = sketch_info.get('sketch_name', sketch_info.get('name', 'UNKNOWN'))
        plane_ref = sketch_info.get('reference_plane', sketch_info.get('plane', sketch_info.get('plane_reference', 'UNKNOWN')))
        
        print(f"✅ Sketch info extracted:")
        print(f"   Name: {sketch_name}")
        print(f"   ID: {sketch_id}")
        print(f"   Plane: {plane_ref}")
        
        if sketch_id == 'UNKNOWN':
            print("❌ Cannot continue without valid sketch_id")
            return
        
        # Step 5: Get initial revision ID (like print(sketch1.revisionId))
        print("\n🔍 Step 5: Get revision ID (print(sketch1.revisionId))...")
        result = client.send_request('fusion.get_sketch_revision_id', {
            'sketch_id': sketch_id
        })
        
        print(f"\n🔍 DEBUG - Revision ID result:")
        print(f"   Type: {type(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ Failed to get revision ID: {result['error']}")
            return
        
        if 'result' in result and isinstance(result['result'], dict):
            revision_result = result['result']
            if 'error' in revision_result:
                print(f"❌ Error in revision result: {revision_result['error']}")
                return
            # Try multiple possible field names for revision
            initial_revision = revision_result.get('revision_id', 
                              revision_result.get('revisionId',
                              revision_result.get('revision', 'UNKNOWN')))
        else:
            print("❌ Unexpected revision response structure")
            return
            
        print(f"✅ Initial revision extracted: {initial_revision}")
        
        # Step 6: Create ObjectCollection (like points = adsk.core.ObjectCollection.create())
        print("\n📦 Step 6: Create ObjectCollection (ObjectCollection.create())...")
        print("🔍 Testing ObjectCollection creation with detailed logging...")
        result = client.send_request('fusion.create_object_collection')
        
        print(f"\n🔍 DEBUG - ObjectCollection result:")
        print(f"   Type: {type(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ ObjectCollection creation failed: {result['error']}")
            print("🔍 This will help us understand why ObjectCollection.create() fails.")
            # Continue anyway to test other components
        elif 'result' in result and isinstance(result['result'], dict):
            collection_result = result['result']
            if 'error' in collection_result:
                print(f"❌ Error in collection result: {collection_result['error']}")
            else:
                collection_info = collection_result
                # Safe field extraction for collection
                coll_id = collection_info.get('collection_id', collection_info.get('id', 'UNKNOWN'))
                coll_type = collection_info.get('collection_type', collection_info.get('type', 'UNKNOWN'))
                item_count = collection_info.get('item_count', collection_info.get('count', 'UNKNOWN'))
                
                print(f"✅ ObjectCollection info:")
                print(f"   ID: {coll_id}")
                print(f"   Type: {coll_type}")
                print(f"   Item count: {item_count}")
        else:
            print("❌ Unexpected collection response structure")
        
        # Step 7: Create Point3D objects (like points.add(Point3D.create(x, y, z)))
        print("\n📍 Step 7: Create Point3D objects (Point3D.create())...")
        spline_points = [
            {'x': -5, 'y': 0, 'z': 0},
            {'x': 5, 'y': 1, 'z': 0},
            {'x': 6, 'y': 4, 'z': 3},
            {'x': 7, 'y': 6, 'z': 6},
            {'x': 2, 'y': 3, 'z': 0},
            {'x': 0, 'y': 1, 'z': 0}
        ]
        
        created_points = []
        for i, point_data in enumerate(spline_points):
            result = client.send_request('fusion.create_point3d', point_data)
            
            if i == 0:  # Debug first point creation
                print(f"\n🔍 DEBUG - Point3D creation result (point {i}):")
                print(f"   Type: {type(result)}")
                print(f"   Raw result: {result}")
                
                if isinstance(result, dict):
                    print(f"   Keys: {list(result.keys())}")
                    for key, value in result.items():
                        print(f"   {key}: {value} (type: {type(value)})")
                
                input("\n⏸️ PAUSE - Press Enter to continue...")
            
            if 'error' in result:
                print(f"❌ Failed to create Point3D {i}: {result['error']}")
                return
            
            if 'result' in result and isinstance(result['result'], dict):
                point_result = result['result']
                if 'error' in point_result:
                    print(f"❌ Error in point result {i}: {point_result['error']}")
                    return
                point_info = point_result
            else:
                print(f"❌ Unexpected point response structure for point {i}")
                return
                
            # Safe coordinate extraction
            coords = point_info.get('coordinates', {})
            if isinstance(coords, dict):
                x = coords.get('x', 'UNKNOWN')
                y = coords.get('y', 'UNKNOWN') 
                z = coords.get('z', 'UNKNOWN')
            else:
                x = y = z = 'UNKNOWN'
                
            created_points.append(point_info)
            print(f"   ✅ Point {i}: ({x}, {y}, {z})")
        
        print(f"✅ Created {len(created_points)} Point3D objects")
        
        # Step 8: Create fitted spline (like sketch1.sketchCurves.sketchFittedSplines.add(points))
        print("\n🌊 Step 8: Create fitted spline (sketchFittedSplines.add(points))...")
        result = client.send_request('fusion.create_fitted_spline_from_points', {
            'sketch_id': sketch_id,
            'points': spline_points
        })
        
        print(f"\n🔍 DEBUG - Fitted spline result:")
        print(f"   Type: {type(result)}")
        print(f"   Raw result: {result}")
        
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   {key}: {value} (type: {type(value)})")
        
        input("\n⏸️ PAUSE - Press Enter to continue...")
        
        if 'error' in result:
            print(f"❌ Failed to create fitted spline: {result['error']}")
            return
        
        if 'result' in result and isinstance(result['result'], dict):
            spline_result = result['result']
            if 'error' in spline_result:
                print(f"❌ Error in spline result: {spline_result['error']}")
                return
            spline_info = spline_result
        else:
            print("❌ Unexpected spline response structure")
            return
            
        # Safe field extraction - no assumptions about field names
        entity_id = spline_info.get('entity_id', spline_info.get('id', 'UNKNOWN'))
        point_count = spline_info.get('point_count', 'UNKNOWN')
        collection_count = spline_info.get('collection_count', 'UNKNOWN')
        initial_rev = spline_info.get('initial_revision_id', 'UNKNOWN')
        final_rev = spline_info.get('final_revision_id', 'UNKNOWN')
        
        print(f"✅ Fitted spline info:")
        print(f"   Entity ID: {entity_id}")
        print(f"   Point count: {point_count}")
        print(f"   Collection count: {collection_count}")
        print(f"   Revision: {initial_rev} → {final_rev}")
        
        # Step 9: Get revision ID after spline (like print(sketch1.revisionId))
        print("\n🔍 Step 9: Get revision ID after spline...")
        result = client.send_request('fusion.get_sketch_revision_id', {
            'sketch_id': sketch_id
        })
        if 'error' in result:
            print(f"❌ Failed to get revision ID: {result['error']}")
            return
        
        spline_revision = result['result']['revision_id']
        print(f"✅ Revision after spline: {spline_revision}")
        
        # Step 10: Create Point3D objects for rectangle (like Point3D.create(0, 0, 0))
        print("\n📍 Step 10: Create rectangle points (Point3D.create())...")
        start_point_data = {'x': 0, 'y': 0, 'z': 0}
        end_point_data = {'x': 5.0, 'y': 5.0, 'z': 0}
        
        result = client.send_request('fusion.create_point3d', start_point_data)
        if 'error' in result:
            print(f"❌ Failed to create start point: {result['error']}")
            return
        start_point_info = result['result']
        print(f"   ✅ Start point: ({start_point_info['coordinates']['x']}, {start_point_info['coordinates']['y']}, {start_point_info['coordinates']['z']})")
        
        result = client.send_request('fusion.create_point3d', end_point_data)
        if 'error' in result:
            print(f"❌ Failed to create end point: {result['error']}")
            return
        end_point_info = result['result']
        print(f"   ✅ End point: ({end_point_info['coordinates']['x']}, {end_point_info['coordinates']['y']}, {end_point_info['coordinates']['z']})")
        
        # Step 11: Create rectangle (like sketchLines.addTwoPointRectangle(startPoint, endPoint))
        print("\n📦 Step 11: Create rectangle (addTwoPointRectangle())...")
        result = client.send_request('fusion.add_two_point_rectangle', {
            'sketch_id': sketch_id,
            'start_point': start_point_data,
            'end_point': end_point_data
        })
        if 'error' in result:
            print(f"❌ Failed to create rectangle: {result['error']}")
            return
        
        rectangle_info = result['result']
        print(f"✅ Rectangle created with {rectangle_info['line_count']} lines")
        print(f"   Method: {rectangle_info['method']}")
        print(f"   Line IDs: {rectangle_info['entity_ids']}")
        print(f"   Revision: {rectangle_info['initial_revision_id']} → {rectangle_info['final_revision_id']}")
        
        # Step 12: Get final revision ID (like print(sketch1.revisionId))
        print("\n🔍 Step 12: Get final revision ID...")
        result = client.send_request('fusion.get_sketch_revision_id', {
            'sketch_id': sketch_id
        })
        if 'error' in result:
            print(f"❌ Failed to get final revision ID: {result['error']}")
            return
        
        final_revision = result['result']['revision_id']
        print(f"✅ Final revision ID: {final_revision}")
        
        # Summary
        print(f"\n🎉 EXACT EXAMPLE SCRIPT COMPLETED!")
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   Document: {doc_name}")
        print(f"   Sketch: {sketch_name} on YZ plane")
        print(f"   Spline: {point_count} points")
        print(f"   Rectangle: {rectangle_info.get('line_count', 'UNKNOWN')} lines")
        print(f"   Revisions: {initial_revision} → {spline_revision} → {final_revision}")
        print(f"\n✅ All steps from original example successfully replicated via MCP!")
        print("🔍 DEBUG: About to exit try block normally...")
        
    except Exception as e:
        print(f"💥 Test failed with exception: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        print(f"🔍 DEBUG: Exception args: {e.args}")
        import traceback
        print("🔍 DEBUG: Full traceback:")
        traceback.print_exc()
        
    finally:
        print("🔍 DEBUG: Entering finally block...")
        try:
            print("🔍 DEBUG: About to call client.close()...")
            client.close()
            print("🔍 DEBUG: client.close() completed successfully")
        except Exception as close_error:
            print(f"🔍 DEBUG: Error during client.close(): {type(close_error).__name__}: {str(close_error)}")
            import traceback
            print("🔍 DEBUG: Close error traceback:")
            traceback.print_exc()
        
        print("🔌 Connection cleanup completed")
        print("🔍 DEBUG: Exiting finally block...")
        print("🔍 DEBUG: Function about to return...")

if __name__ == "__main__":
    print("🔍 DEBUG: Starting main execution...")
    try:
        test_exact_example_workflow()
        print("🔍 DEBUG: test_exact_example_workflow() completed normally")
    except Exception as main_error:
        print(f"🔍 DEBUG: Exception in main: {type(main_error).__name__}: {str(main_error)}")
        import traceback
        print("🔍 DEBUG: Main exception traceback:")
        traceback.print_exc()
    
    print("🔍 DEBUG: Script execution completed, about to exit...")
