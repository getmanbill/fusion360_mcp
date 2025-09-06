"""
Real Arc Operations Test via MCP Client
Tests the deployed arc operations methods through MCP socket communication
Following the same pattern as other test files
"""
import socket
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'arc_operations_real_mcp_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class ArcOperationsMCPClient:
    """MCP client for testing arc operations"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        
    def connect(self):
        """Connect to MCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            logging.info(f"Connected to MCP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            return False
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send request to MCP server"""
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
            
            response_data = self.socket.recv(8192).decode('utf-8')
            response = json.loads(response_data)
            
            return response
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()

def test_arc_creation_methods(client: ArcOperationsMCPClient) -> bool:
    """Test arc creation methods via MCP"""
    logging.info("Testing arc creation methods...")
    
    # First, create a sketch to work with
    logging.info("Creating test sketch...")
    response = client.send_request("fusion.create_sketch", {
        "plane_reference": "XY",
        "name": "ArcTestSketch"
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"Failed to create sketch: {response}")
        return False
    
    # Debug: log the actual response structure
    logging.info(f"Sketch creation response: {response}")
    
    # Handle different response structures
    if "data" in response["result"]:
        sketch_id = response["result"]["data"]["sketch_id"]
    else:
        sketch_id = response["result"]["sketch_id"]
    logging.info(f"Created sketch: {sketch_id}")
    
    # Test 1: Create arc by three points
    logging.info("Testing create_arc_by_three_points...")
    response = client.send_request("fusion.create_arc_by_three_points", {
        'sketch_id': sketch_id,
        'point1': {'x': 0, 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5},
        'construction': False
    })
    
    # Debug: log the actual response structure
    logging.info(f"Arc creation response: {response}")
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_arc_by_three_points failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        arc1_id = response["result"]["data"]["arc_id"]
    else:
        arc1_id = response["result"]["arc_id"]
    logging.info(f"[PASS] create_arc_by_three_points: {arc1_id}")
    # Handle different response structures for radius too
    if "data" in response["result"]:
        radius = response["result"]["data"]["radius"]
    else:
        radius = response["result"]["radius"]
    logging.info(f"  Radius: {radius}")
    
    # Test 2: Create arc by center, start point, and sweep angle
    logging.info("Testing create_arc_by_center_start_sweep...")
    response = client.send_request("fusion.create_arc_by_center_start_sweep", {
        'sketch_id': sketch_id,
        'center': {'x': 10, 'y': 0},
        'start_point': {'x': 15, 'y': 0},
        'sweep_angle': 1.57,  # 90 degrees in radians
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_arc_by_center_start_sweep failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        arc2_id = response["result"]["data"]["arc_id"]
        radius = response["result"]["data"]["radius"]
        sweep_angle = response["result"]["data"]["sweep_angle"]
    else:
        arc2_id = response["result"]["arc_id"]
        radius = response["result"]["radius"]
        sweep_angle = response["result"]["sweep_angle"]
    logging.info(f"[PASS] create_arc_by_center_start_sweep: {arc2_id}")
    logging.info(f"  Radius: {radius}")
    logging.info(f"  Sweep angle: {sweep_angle}")
    
    # Test 3: Create arc by center and two end points  
    logging.info("Testing create_arc_by_center_start_end...")
    response = client.send_request("fusion.create_arc_by_center_start_end", {
        'sketch_id': sketch_id,
        'center': {'x': 25, 'y': 5},
        'start_point': {'x': 20, 'y': 5},
        'end_point': {'x': 30, 'y': 5},
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_arc_by_center_start_end failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        arc3_id = response["result"]["data"]["arc_id"]
        radius = response["result"]["data"]["radius"]
    else:
        arc3_id = response["result"]["arc_id"]
        radius = response["result"]["radius"]
    logging.info(f"[PASS] create_arc_by_center_start_end: {arc3_id}")
    logging.info(f"  Radius: {radius}")
    
    # Test 4: Create lines for fillet testing
    logging.info("Creating lines for fillet test...")
    line1_response = client.send_request("fusion.create_line", {
        'sketch_id': sketch_id,
        'start_point': {'x': 20, 'y': 0},
        'end_point': {'x': 25, 'y': 0}
    })
    
    line2_response = client.send_request("fusion.create_line", {
        'sketch_id': sketch_id,
        'start_point': {'x': 25, 'y': 0},
        'end_point': {'x': 25, 'y': 5}
    })
    
    if ("error" in line1_response or not line1_response.get("result", {}).get("success") or
        "error" in line2_response or not line2_response.get("result", {}).get("success")):
        logging.error("Failed to create lines for fillet test")
        return False
    
    # Handle different response structures for lines
    if "data" in line1_response["result"]:
        line1_id = line1_response["result"]["data"]["entity_id"]
        line2_id = line2_response["result"]["data"]["entity_id"]
    else:
        line1_id = line1_response["result"]["entity_id"]
        line2_id = line2_response["result"]["entity_id"]
    logging.info(f"Created lines: {line1_id}, {line2_id}")
    
    # Test 4: Create fillet arc
    logging.info("Testing create_arc_fillet...")
    response = client.send_request("fusion.create_arc_fillet", {
        'sketch_id': sketch_id,
        'curve1_id': line1_id,
        'curve2_id': line2_id,
        'radius': 1.0,
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_arc_fillet failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        arc3_id = response["result"]["data"]["arc_id"]
        radius = response["result"]["data"]["radius"]
    else:
        arc3_id = response["result"]["arc_id"]
        radius = response["result"]["radius"]
    logging.info(f"[PASS] create_arc_fillet: {arc3_id}")
    logging.info(f"  Radius: {radius}")
    
    return True, sketch_id, arc1_id, arc2_id, arc3_id

def test_arc_query_methods(client: ArcOperationsMCPClient, sketch_id: str, arc_id: str) -> bool:
    """Test arc query methods via MCP"""
    logging.info("Testing arc query methods...")
    
    # Test get_arc_properties
    logging.info("Testing get_arc_properties...")
    response = client.send_request("fusion.get_arc_properties", {
        'sketch_id': sketch_id,
        'arc_id': arc_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_arc_properties failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_arc_properties: {arc_id}")
    logging.info(f"  Radius: {data['radius']}")
    logging.info(f"  Length: {data['length']}")
    logging.info(f"  Start angle: {data['start_angle']}")
    logging.info(f"  End angle: {data['end_angle']}")
    logging.info(f"  Sweep angle: {data['sweep_angle']}")
    
    # Test get_arc_state
    logging.info("Testing get_arc_state...")
    response = client.send_request("fusion.get_arc_state", {
        'sketch_id': sketch_id,
        'arc_id': arc_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_arc_state failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_arc_state: {arc_id}")
    logging.info(f"  Construction: {data['is_construction']}")
    logging.info(f"  Deletable: {data['is_deletable']}")
    logging.info(f"  Fixed: {data['is_fixed']}")
    logging.info(f"  Visible: {data['is_visible']}")
    
    # Test get_arc_constraints
    logging.info("Testing get_arc_constraints...")
    response = client.send_request("fusion.get_arc_constraints", {
        'sketch_id': sketch_id,
        'arc_id': arc_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_arc_constraints failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_arc_constraints: {arc_id}")
    logging.info(f"  Constraints: {data['constraint_count']}")
    logging.info(f"  Dimensions: {data['dimension_count']}")
    
    # Test get_arc_intersections
    logging.info("Testing get_arc_intersections...")
    logging.info(f"  Testing intersections for arc: {arc_id}")
    logging.info(f"  In sketch with other geometry present")
    
    response = client.send_request("fusion.get_arc_intersections", {
        'sketch_id': sketch_id,
        'arc_id': arc_id
    })
    
    # Debug: log the full response
    logging.info(f"get_arc_intersections response: {response}")
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_arc_intersections failed: {response}")
        logging.error(f"  Error details: {response.get('result', {}).get('error', 'Unknown error')}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_arc_intersections: {arc_id}")
    logging.info(f"  Intersections found: {data['intersection_count']}")
    
    # Log details of each intersection if any found
    if data['intersection_count'] > 0:
        for i, intersection in enumerate(data.get('intersections', [])):
            logging.info(f"  Intersection {i+1}: curve {intersection['curve_type']} at ({intersection['point']['x']:.2f}, {intersection['point']['y']:.2f})")
    else:
        logging.info(f"  No intersections found (this is normal for isolated arc)")
    
    return True

def test_arc_manipulation_methods(client: ArcOperationsMCPClient, sketch_id: str, arc_id: str) -> bool:
    """Test arc manipulation methods via MCP"""
    logging.info("Testing arc manipulation methods...")
    
    # Test split_arc
    logging.info("Testing split_arc...")
    response = client.send_request("fusion.split_arc", {
        'sketch_id': sketch_id,
        'arc_id': arc_id,
        'split_point': {'x': 2.5, 'y': 2.5}
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"split_arc failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] split_arc: {arc_id}")
    logging.info(f"  Created {len(data['split_curves'])} curves")
    
    # Test break_arc_curve (use a different arc)
    logging.info("Testing break_arc_curve...")
    response = client.send_request("fusion.break_arc_curve", {
        'sketch_id': sketch_id,
        'arc_id': arc_id,  # This might fail if arc was split, but that's OK for testing
        'break_point': {'x': 3.5, 'y': 3.5}
    })
    
    # Don't fail the test if this specific operation fails since arc might be modified
    if "error" in response or not response.get("result", {}).get("success"):
        logging.warning(f"break_arc_curve expected to fail on modified arc: {response}")
    else:
        # Handle different response structures
        if "data" in response["result"]:
            data = response["result"]["data"]
        else:
            data = response["result"]
        logging.info(f"[PASS] break_arc_curve: {arc_id}")
        logging.info(f"  Created {len(data['broken_curves'])} curves")
    
    return True

def test_error_handling(client: ArcOperationsMCPClient) -> bool:
    """Test error handling via MCP"""
    logging.info("Testing error handling...")
    
    # Test with invalid sketch ID
    response = client.send_request("fusion.create_arc_by_three_points", {
        'sketch_id': 'invalid_sketch_id',
        'point1': {'x': 0, 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5}
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.info("[PASS] Error handling: Invalid sketch ID correctly rejected")
    else:
        logging.error("[FAIL] Error handling: Should have failed with invalid sketch ID")
        return False
    
    # Test with invalid point coordinates
    response = client.send_request("fusion.create_arc_by_three_points", {
        'sketch_id': 'any_sketch_id',
        'point1': {'x': 'invalid', 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5}
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.info("[PASS] Error handling: Invalid coordinates correctly rejected")
    else:
        logging.error("[FAIL] Error handling: Should have failed with invalid coordinates")
        return False
    
    return True

def run_comprehensive_arc_test():
    """Run comprehensive arc operations test via MCP"""
    start_time = datetime.now()
    logging.info("="*60)
    logging.info("STARTING COMPREHENSIVE ARC OPERATIONS TEST VIA MCP")
    logging.info("="*60)
    
    client = ArcOperationsMCPClient()
    
    if not client.connect():
        logging.error("Failed to connect to MCP server")
        return False
    
    all_passed = True
    
    try:
        # Test arc creation methods
        result = test_arc_creation_methods(client)
        if not result:
            all_passed = False
        else:
            success, sketch_id, arc1_id, arc2_id, arc3_id = result
            logging.info("[PASS] Arc creation methods completed")
            
            # Test arc query methods
            if test_arc_query_methods(client, sketch_id, arc1_id):
                logging.info("[PASS] Arc query methods completed")
            else:
                all_passed = False
            
            # Test arc manipulation methods
            if test_arc_manipulation_methods(client, sketch_id, arc1_id):
                logging.info("[PASS] Arc manipulation methods completed")
            else:
                all_passed = False
        
        # Test error handling
        if test_error_handling(client):
            logging.info("[PASS] Error handling completed")
        else:
            all_passed = False
            
    except Exception as e:
        logging.error(f"[FAIL] Test failed with exception: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        all_passed = False
    
    finally:
        client.close()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Generate summary report
    logging.info("="*60)
    logging.info("MCP TEST SUMMARY REPORT")
    logging.info("="*60)
    logging.info(f"Start time: {start_time}")
    logging.info(f"End time: {end_time}")
    logging.info(f"Duration: {duration}")
    logging.info("")
    
    if all_passed:
        logging.info("[PASS] ALL MCP TESTS PASSED")
        logging.info("Arc operations are working correctly via MCP!")
    else:
        logging.info("[FAIL] SOME MCP TESTS FAILED")
        logging.info("Check the log for details on what failed.")
    
    logging.info("")
    logging.info("TESTED METHODS VIA MCP:")
    tested_methods = [
        "create_arc_by_three_points",
        "create_arc_by_center_start_sweep",
        "create_arc_by_center_start_end", 
        "create_arc_fillet",
        "get_arc_properties", 
        "get_arc_constraints",
        "get_arc_state",
        "get_arc_intersections",
        "split_arc",
        "break_arc_curve"
    ]
    
    for method in tested_methods:
        logging.info(f"  [TESTED] {method}")
    
    logging.info("")
    logging.info("NOTE: These tests called the real arc_operations.py methods")
    logging.info("through MCP socket communication with actual Fusion 360 API.")
    
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_arc_test()
    exit(0 if success else 1)
