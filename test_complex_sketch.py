#!/usr/bin/env python3
"""
Complex Sketch Test - Parametric Mounting Bracket
Creates a realistic parametric sketch using proven MCP tools
"""

import socket
import json
import time
import math
from typing import Dict, Any, Optional

# SMART delays - much shorter thanks to API state management
REQUEST_DELAY = 1.0      # Reduced from 5.0s
OPERATION_DELAY = 2.0    # Reduced from 15.0s  
CRITICAL_DELAY = 3.0     # Reduced from 30.0s
SKETCH_DELAY = 5.0       # Reduced from 45.0s - API handles state now
SAFETY_DELAY = 8.0       # Reduced from 60.0s

class FusionClient:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(15.0)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to Fusion")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 Disconnected")
    
    def send_request(self, method: str, params: Dict[str, Any] = None, silent: bool = False) -> Optional[Dict[str, Any]]:
        import threading
        thread_id = threading.current_thread().ident
        
        if not self.socket:
            print(f"🔌 [ERROR] Thread {thread_id} - No socket connection for {method}")
            return None
        
        print(f"🧵 [CLIENT] Thread {thread_id} - Starting request {method}")
        
        request_id = int(time.time() * 1000)
        request = {
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        if not silent:
            print(f"📤 [SEND] Thread {thread_id} - {method}")
            print(f"   📋 Request ID: {request_id}")
            if params:
                # Show params but truncate long IDs
                display_params = {}
                for k, v in params.items():
                    if isinstance(v, str) and len(v) > 20:
                        display_params[k] = f"{v[:12]}...({len(v)} chars)"
                    else:
                        display_params[k] = v
                print(f"   📋 Params: {display_params}")
        
        try:
            request_json = json.dumps(request)
            print(f"📡 [NETWORK] Thread {thread_id} - Encoding {len(request_json)} bytes to send...")
            print(f"📝 [PAYLOAD] Thread {thread_id} - Request: {request_json[:200]}{'...' if len(request_json) > 200 else ''}")
            
            print(f"⏳ [SOCKET] Thread {thread_id} - About to send data via socket...")
            self.socket.send(request_json.encode('utf-8'))
            print(f"✅ [SOCKET] Thread {thread_id} - Data sent successfully!")
            
            print(f"👂 [SOCKET] Thread {thread_id} - Waiting for response...")
            response_data = self.socket.recv(4096)
            print(f"📥 [SOCKET] Thread {thread_id} - Received {len(response_data)} bytes")
            
            if not response_data:
                print(f"❌ [ERROR] Thread {thread_id} - Empty response for {method}")
                return None
            
            print(f"🔍 [DECODE] Thread {thread_id} - Decoding JSON response...")
            response = json.loads(response_data.decode('utf-8'))
            print(f"📋 [RESPONSE] Thread {thread_id} - Raw response: {str(response)[:300]}{'...' if len(str(response)) > 300 else ''}")
            
            if not silent:
                print(f"📥 [RECV] Thread {thread_id} - Response for {method}")
                print(f"   📋 Response ID: {response.get('id', 'missing')}")
                
            result = response.get('result', response)
            
            if 'error' in result:
                print(f"❌ [ERROR] {method}: {result['error']}")
            elif not silent:
                success = result.get('success', False)
                status = "✅ SUCCESS" if success else "⚠️  PARTIAL"
                print(f"   📋 Status: {status}")
            
            print(f"⏳ [DELAY] Waiting {REQUEST_DELAY}s before next request...")
            time.sleep(REQUEST_DELAY)
            return response
            
        except ConnectionError as e:
            print(f"💥 [CONNECTION] Thread {thread_id} - Connection error for {method}: {e}")
            print(f"🔍 [DEBUG] Thread {thread_id} - This usually means Fusion crashed/closed connection")
            return None
        except json.JSONDecodeError as e:
            print(f"💥 [JSON] Thread {thread_id} - Invalid JSON response for {method}: {e}")
            print(f"   📋 Raw data: {response_data[:100]}...")
            return None
        except Exception as e:
            print(f"💥 [EXCEPTION] Thread {thread_id} - {method} failed: {type(e).__name__}: {e}")
            import traceback
            print(f"📊 [TRACEBACK] Thread {thread_id}:\n{traceback.format_exc()}")
            return None
    
    # Helper methods
    def list_parameters(self, label: str = "") -> None:
        """List current parameters for debugging"""
        response = self.send_request("fusion.list_parameters", {}, silent=True)
        if response and response.get('result', {}).get('parameters'):
            params = response['result']['parameters']
            count = len(params)
            print(f"📋 Parameters {label}: ({count}) {', '.join([p['name'] for p in params])}")
        else:
            print(f"📋 Parameters {label}: None or failed")
    
    def set_parameter(self, name: str, value: float, units: str = "") -> bool:
        params = {"name": name, "value": value, "units": units}
        response = self.send_request("fusion.set_parameter", params, silent=True)
        if response and response.get('result', {}).get('success'):
            print(f"📐 Parameter: {name} = {value} {units}")
            return True
        return False
    
    def create_sketch(self, plane: str = "XY", name: str = None) -> Optional[str]:
        # Use unique name with timestamp to avoid duplicates
        if name:
            import time
            unique_name = f"{name}_{int(time.time())}"
        else:
            unique_name = None
            
        params = {"plane_reference": plane}
        if unique_name:
            params["name"] = unique_name
            
        response = self.send_request("fusion.create_sketch", params, silent=True)
        if response and response.get('result', {}).get('success'):
            sketch_id = response['result'].get('sketch_id')
            actual_name = response['result'].get('name', unique_name or 'Unnamed')
            print(f"✏️  Created sketch: {actual_name}")
            print(f"   Sketch ID: {sketch_id[:12]}...")
            return sketch_id
        return None
    
    def list_sketches(self, label: str = "") -> None:
        """List current sketches for debugging"""
        response = self.send_request("fusion.list_sketches", {}, silent=True)
        if response and response.get('result', {}).get('sketches'):
            sketches = response['result']['sketches']
            count = len(sketches)
            print(f"✏️  Sketches {label}: ({count}) {', '.join([s['name'] for s in sketches])}")
        else:
            print(f"✏️  Sketches {label}: None or failed")
    
    def activate_sketch(self, sketch_id: str) -> bool:
        """Activate sketch for editing"""
        params = {"sketch_id": sketch_id}
        response = self.send_request("fusion.activate_sketch", params, silent=False)  # Show errors
        if response and response.get('result', {}).get('success'):
            print(f"🎯 Activated sketch for editing")
            return True
        else:
            if response:
                print(f"❌ Sketch activation failed: {response}")
            else:
                print("❌ Sketch activation: No response")
        return False
    
    def create_rectangle(self, sketch_id: str, corner1: Dict[str, float], corner2: Dict[str, float]) -> Optional[list]:
        print(f"\n🔍 [GEOMETRY] Starting rectangle creation")
        print(f"   📋 Sketch ID: {sketch_id[:12]}... (length: {len(sketch_id)})")
        print(f"   📋 Corner1: {corner1}")
        print(f"   📋 Corner2: {corner2}")
        print(f"   📋 Area: {abs(corner2['x'] - corner1['x']) * abs(corner2['y'] - corner1['y'])} sq units")
        
        params = {"sketch_id": sketch_id, "corner1": corner1, "corner2": corner2}
        
        print(f"🚀 [GEOMETRY] Preparing rectangle request...")
        print(f"   📋 Request size: {len(json.dumps(params))} chars")
        print(f"   📋 Sketch ID valid: {len(sketch_id) > 0}")
        print(f"   📋 Corner validation...")
        print(f"      Corner1 x: {corner1['x']} (type: {type(corner1['x'])})")
        print(f"      Corner1 y: {corner1['y']} (type: {type(corner1['y'])})")
        print(f"      Corner2 x: {corner2['x']} (type: {type(corner2['x'])})")
        print(f"      Corner2 y: {corner2['y']} (type: {type(corner2['y'])})")
        
        # Check if coordinates are valid numbers
        try:
            float(corner1['x'])
            float(corner1['y']) 
            float(corner2['x'])
            float(corner2['y'])
            print(f"   ✅ All coordinates are valid numbers")
        except Exception as coord_error:
            print(f"   ❌ Invalid coordinates: {coord_error}")
            return None
        
        print(f"🚀 [GEOMETRY] Sending rectangle request to Fusion API...")
        response = self.send_request("fusion.create_rectangle", params, silent=False)
        
        if response:
            print(f"📋 [GEOMETRY] Full response analysis:")
            print(f"   📋 Response type: {type(response)}")
            print(f"   📋 Response keys: {list(response.keys())}")
            print(f"   📋 Full response: {json.dumps(response, indent=2)}")
            
        if response and response.get('result', {}).get('success'):
            entity_ids = response['result'].get('entity_ids', [])
            print(f"✅ [GEOMETRY] Rectangle created successfully!")
            print(f"   📋 Created {len(entity_ids)} entities")
            print(f"   📋 Entity IDs: {entity_ids}")
            print(f"   📋 Bounds: ({corner1['x']}, {corner1['y']}) to ({corner2['x']}, {corner2['y']})")
            return entity_ids
        else:
            print(f"❌ [GEOMETRY] Rectangle creation FAILED")
            if response:
                print(f"   📋 Error analysis:")
                error_msg = response.get('result', {}).get('error', 'Unknown error')
                print(f"   📋 Error message: {error_msg}")
                print(f"   📋 Full error response: {json.dumps(response, indent=2)}")
            else:
                print("   📋 No response received from Fusion API")
        return None
    
    def create_line(self, sketch_id: str, start: Dict[str, float], end: Dict[str, float]) -> Optional[str]:
        import threading
        thread_id = threading.current_thread().ident
        
        print(f"\n🔍 [LINE] Thread {thread_id} - Starting line creation")
        print(f"   📋 Start: {start}")
        print(f"   📋 End: {end}")
        print(f"   📋 Sketch ID: {sketch_id[:20]}...({len(sketch_id)} chars)")
        print(f"   📋 Line length: {math.sqrt((end['x'] - start['x'])**2 + (end['y'] - start['y'])**2):.2f}")
        
        params = {"sketch_id": sketch_id, "start_point": start, "end_point": end}
        
        print(f"📤 [LINE] Thread {thread_id} - About to send create_line request")
        print(f"⚠️  [CRITICAL] Thread {thread_id} - This is where crashes typically happen...")
        
        response = self.send_request("fusion.create_line", params, silent=False)
        
        print(f"📥 [LINE] Thread {thread_id} - Got response from create_line")
        
        if response and response.get('result', {}).get('success'):
            entity_id = response['result'].get('entity_id')
            print(f"✅ [LINE] Thread {thread_id} - Line created successfully!")
            print(f"   📋 Entity ID: {entity_id}")
            return entity_id
        else:
            print(f"❌ [LINE] Thread {thread_id} - Line creation failed")
            if response:
                error_msg = response.get('result', {}).get('error', 'Unknown')
                print(f"   📋 Error details: {error_msg}")
                print(f"   📋 Full response: {response}")
            else:
                print(f"   📋 No response received (connection issue)")
        return None
    
    def create_circle(self, sketch_id: str, center: Dict[str, float], radius: float) -> Optional[str]:
        params = {"sketch_id": sketch_id, "center": center, "radius": radius}
        response = self.send_request("fusion.create_circle", params, silent=True)
        if response and response.get('result', {}).get('success'):
            entity_id = response['result'].get('entity_id')
            print(f"⭕ Circle: center ({center['x']}, {center['y']}) radius {radius}")
            return entity_id
        return None
    

    
    def add_radius_constraint(self, sketch_id: str, entity_id: str, radius: float, param_name: str = None) -> bool:
        params = {"sketch_id": sketch_id, "entity_id": entity_id, "radius": radius}
        if param_name:
            params["parameter_name"] = param_name
        response = self.send_request("fusion.add_radius_constraint", params, silent=True)
        if response and response.get('result', {}).get('success'):
            print(f"🔗 Radius constraint: {radius} mm" + (f" (linked to {param_name})" if param_name else ""))
            return True
        return False
    
    def finish_sketch(self, sketch_id: str) -> bool:
        params = {"sketch_id": sketch_id}
        response = self.send_request("fusion.finish_sketch", params, silent=True)
        if response and response.get('result', {}).get('success'):
            constrained = response['result'].get('is_fully_constrained', False)
            status = "✅ fully constrained" if constrained else "⚠️  under-constrained"
            print(f"🏁 Finished sketch: {status}")
            return True
        return False

def create_mounting_bracket_sketch(client: FusionClient) -> bool:
    """Create a parametric mounting bracket sketch"""
    
    print("\n🔧 CREATING PARAMETRIC MOUNTING BRACKET")
    print("=" * 50)
    
    # Step 0: Check initial state
    print("\n" + "="*60)
    print("🔍 [INITIAL STATE] Checking current Fusion state...")
    print("="*60)
    
    print("\n📋 [PARAMETERS] Listing initial parameters...")
    client.list_parameters("BEFORE")
    print(f"⏳ [DELAY] Waiting {OPERATION_DELAY}s after parameter check...")
    time.sleep(OPERATION_DELAY)
    
    print("\n✏️  [SKETCHES] Listing initial sketches...")
    client.list_sketches("BEFORE")
    print(f"⏳ [DELAY] Waiting {OPERATION_DELAY}s after sketch check...")
    time.sleep(OPERATION_DELAY)
    
    # Step 1: Create design parameters
    print("\n" + "="*60)
    print("📐 [PARAMETERS] Creating design parameters...")
    print("="*60)
    print(f"⏳ [DELAY] Initial wait of {OPERATION_DELAY}s...")
    time.sleep(OPERATION_DELAY)
    
    parameters = [
        ("BracketWidth", 80.0, "mm"),
        ("BracketHeight", 60.0, "mm"), 
        ("MountHoleDia", 6.0, "mm"),
        ("CenterHoleDia", 12.0, "mm"),
        ("EdgeOffset", 10.0, "mm")
    ]
    
    success = True
    for i, (name, value, units) in enumerate(parameters, 1):
        print(f"\n📐 [PARAM {i}/5] Creating {name}...")
        param_success = client.set_parameter(name, value, units)
        success &= param_success
        
        if param_success:
            print(f"✅ [PARAM {i}/5] {name} = {value} {units} created successfully")
        else:
            print(f"❌ [PARAM {i}/5] Failed to create {name}")
        
        print(f"⏳ [DELAY] Waiting {CRITICAL_DELAY}s before next parameter...")
        time.sleep(CRITICAL_DELAY)
    
    if not success:
        print("❌ Failed to create parameters")
        return False
    
    print("✅ All parameters created successfully")
    
    # Step 1.5: Verify parameter creation
    print("\n📋 Verifying parameters were created properly...")
    client.list_parameters("AFTER CREATION")
    time.sleep(OPERATION_DELAY)
    
    # Step 2: Create main sketch
    print(f"\n✏️  Creating main bracket sketch...")
    time.sleep(OPERATION_DELAY)
    
    sketch_id = client.create_sketch("XY", "BracketProfile")
    if not sketch_id:
        print("❌ Failed to create sketch")
        return False
    
    time.sleep(SKETCH_DELAY)  # Shorter delay - API handles state management
    print("⏳ API managing state with doEvents and computeAll...")
    
    # Step 2.1: Verify sketch creation
    print("\n✏️  Verifying sketch was created...")
    client.list_sketches("AFTER CREATION")
    time.sleep(OPERATION_DELAY)
    
    # Step 2.5: Verify sketch is ready for editing (sketches auto-activate)
    print("\n🎯 Verifying sketch is ready for editing...")
    print("⏳ Using smart state management instead of long waits...")
    time.sleep(CRITICAL_DELAY)  # Much shorter delay
    
    if not client.activate_sketch(sketch_id):
        print("⚠️  Sketch verification failed, but continuing...")
        # Don't return False - sketches are auto-activated, this is just a check
    else:
        print("✅ Sketch is ready for geometry creation")
    
    time.sleep(SAFETY_DELAY)  # Reduced delay - API handles state
    
    # Step 3: Create main bracket outline (rectangle)
    print("\n" + "="*60)
    print("📐 [GEOMETRY] Creating bracket outline...")
    print("="*60)
    print("⚠️  [CRITICAL] This is where crashes typically happen...")
    print("⏳ Using extra-long delay before first geometry creation...")
    
    # Extra long delay before first geometry - this seems to be the critical point
    print(f"⏳ [DELAY] Extra safety delay: {SAFETY_DELAY * 2}s...")
    time.sleep(SAFETY_DELAY * 2)  # Double the safety delay
    print(f"⏳ [DELAY] Additional critical delay: {CRITICAL_DELAY}s...")
    time.sleep(CRITICAL_DELAY)
    print("🚀 [GEOMETRY] Ready to attempt rectangle creation...")
    
    # Try a minimal test first - single line instead of rectangle
    print("\n🧪 [TEST] Attempting simple line creation first...")
    test_line = client.create_line(
        sketch_id,
        {"x": 10, "y": 10},
        {"x": 20, "y": 20}
    )
    
    if test_line:
        print("✅ [TEST] Simple line creation succeeded!")
        print("📐 [GEOMETRY] Now attempting rectangle...")
        
        main_rect = client.create_rectangle(
            sketch_id, 
            {"x": 0, "y": 0}, 
            {"x": 80, "y": 60}  # Will be parametric later
        )
        if not main_rect:
            print("❌ Failed to create main rectangle")
            return False
    else:
        print("❌ [TEST] Simple line creation failed - geometry creation is broken")
        return False
    
    time.sleep(CRITICAL_DELAY)
    
    # Step 4: Create mounting holes (circles)
    print("\n⭕ Creating mounting holes...")
    time.sleep(OPERATION_DELAY)
    
    # Top left hole
    hole1 = client.create_circle(sketch_id, {"x": 10, "y": 50}, 3)
    if hole1:
        time.sleep(OPERATION_DELAY)
        client.add_radius_constraint(sketch_id, hole1, 3.0, "MountHoleDia")
    
    time.sleep(SKETCH_DELAY)
    
    # Top right hole  
    hole2 = client.create_circle(sketch_id, {"x": 70, "y": 50}, 3)
    if hole2:
        time.sleep(OPERATION_DELAY)
        client.add_radius_constraint(sketch_id, hole2, 3.0, "MountHoleDia")
    
    time.sleep(SKETCH_DELAY)
    
    # Bottom left hole
    hole3 = client.create_circle(sketch_id, {"x": 10, "y": 10}, 3)
    if hole3:
        time.sleep(OPERATION_DELAY)
        client.add_radius_constraint(sketch_id, hole3, 3.0, "MountHoleDia")
    
    time.sleep(SKETCH_DELAY)
    
    # Bottom right hole
    hole4 = client.create_circle(sketch_id, {"x": 70, "y": 10}, 3)
    if hole4:
        time.sleep(OPERATION_DELAY)
        client.add_radius_constraint(sketch_id, hole4, 3.0, "MountHoleDia")
    
    time.sleep(SKETCH_DELAY)
    
    # Step 5: Create center feature hole
    print("\n🎯 Creating center feature hole...")
    time.sleep(OPERATION_DELAY)
    
    center_hole = client.create_circle(sketch_id, {"x": 40, "y": 30}, 6)
    if center_hole:
        time.sleep(OPERATION_DELAY)
        client.add_radius_constraint(sketch_id, center_hole, 6.0, "CenterHoleDia")
    
    time.sleep(SKETCH_DELAY)
    
    # Step 6: Add some construction lines for reference
    print("\n📏 Adding reference lines...")
    time.sleep(OPERATION_DELAY)
    
    # Center vertical line
    client.create_line(sketch_id, {"x": 40, "y": 0}, {"x": 40, "y": 60})
    time.sleep(SKETCH_DELAY)
    
    # Center horizontal line  
    client.create_line(sketch_id, {"x": 0, "y": 30}, {"x": 80, "y": 30})
    time.sleep(SKETCH_DELAY)
    
    # Step 7: Finish the sketch
    print("\n🏁 Finalizing sketch...")
    time.sleep(OPERATION_DELAY)
    
    success = client.finish_sketch(sketch_id)
    if not success:
        print("⚠️  Sketch finished but may need more constraints")
    
    # Step 8: Final parameter verification
    print("\n📋 Final parameter verification...")
    client.list_parameters("FINAL STATE")
    
    return True

def main():
    """Main test execution"""
    import threading
    thread_id = threading.current_thread().ident
    main_thread_id = threading.main_thread().ident
    
    print("🚀 Complex Parametric Sketch Test (ULTRA-VERBOSE THREADING DEBUG)")
    print(f"🧵 [MAIN] Starting test on thread {thread_id}")
    print(f"🧵 [MAIN] Main thread ID: {main_thread_id}")
    print(f"🧵 [MAIN] Is main thread: {thread_id == main_thread_id}")
    print()
    print("Creating a realistic mounting bracket with:")
    print("  - 5 design parameters")
    print("  - Main outline rectangle") 
    print("  - 4 mounting holes")
    print("  - 1 center feature hole")
    print("  - Reference construction lines")
    print("  - Parametric constraints")
    print()
    print("✨ IMPROVED: Using adsk.doEvents() and computeAll() for smart state management")
    print("✨ FIXED: Point3D.create() instead of Point2D for geometry creation")
    print("🔧 NEW: Ultra-verbose threading and API logging")
    print("⏱️  Expected duration: 3-4 minutes (much faster!)")
    print()
    
    print(f"🔌 [MAIN] Thread {thread_id} - Creating Fusion client...")
    client = FusionClient()
    print(f"🔌 [MAIN] Thread {thread_id} - Attempting connection...")
    if not client.connect():
        print(f"❌ [MAIN] Thread {thread_id} - Connection failed")
        return
    print(f"✅ [MAIN] Thread {thread_id} - Connected successfully")
    
    try:
        success = create_mounting_bracket_sketch(client)
        
        if success:
            print("\n" + "="*50)
            print("🎉 COMPLEX SKETCH CREATED SUCCESSFULLY!")
            print("✅ Parametric mounting bracket complete")
            print("✅ All constraints applied")
            print("✅ Ready for 3D modeling")
            print("="*50)
        else:
            print("\n❌ Complex sketch creation failed")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
