"""
Simple Circle Operations Test via MCP Client
Tests basic circle operations following the arc test pattern
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
        logging.FileHandler(f'circle_operations_simple_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class CircleOperationsMCPClient:
    """MCP client for testing circle operations"""
    
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

def test_circle_creation_methods(client: CircleOperationsMCPClient) -> bool:
    """Test circle creation methods via MCP"""
    logging.info("Testing circle creation methods...")
    
    # First, create a sketch to work with
    logging.info("Creating test sketch...")
    response = client.send_request("fusion.create_sketch", {
        "plane_reference": "XY",
        "name": "CircleTestSketch"
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
    
    # Test 1: Create circle by center and radius (new method)
    logging.info("Testing create_circle_by_center_radius...")
    response = client.send_request("fusion.create_circle_by_center_radius", {
        'sketch_id': sketch_id,
        'center': {'x': 0, 'y': 0},
        'radius': 5.0,
        'construction': False
    })
    
    # Debug: log the actual response structure
    logging.info(f"Circle creation response: {response}")
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_circle_by_center_radius failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        circle1_id = response["result"]["data"]["entity_id"]
        radius = response["result"]["data"]["radius"]
    else:
        circle1_id = response["result"]["entity_id"]
        radius = response["result"]["radius"]
    logging.info(f"[PASS] create_circle_by_center_radius: {circle1_id}")
    logging.info(f"  Radius: {radius}")
    
    # Test 2: Create circle by three points
    logging.info("Testing create_circle_by_three_points...")
    response = client.send_request("fusion.create_circle_by_three_points", {
        'sketch_id': sketch_id,
        'point1': {'x': 10, 'y': 0},
        'point2': {'x': 13, 'y': 4},
        'point3': {'x': 10, 'y': 8},
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_circle_by_three_points failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        circle2_id = response["result"]["data"]["entity_id"]
        radius = response["result"]["data"]["radius"]
    else:
        circle2_id = response["result"]["entity_id"]
        radius = response["result"]["radius"]
    logging.info(f"[PASS] create_circle_by_three_points: {circle2_id}")
    logging.info(f"  Radius: {radius}")
    
    # Test 3: Create circle by two points (diameter)
    logging.info("Testing create_circle_by_two_points...")
    response = client.send_request("fusion.create_circle_by_two_points", {
        'sketch_id': sketch_id,
        'point1': {'x': -10, 'y': -5},
        'point2': {'x': -10, 'y': 5},
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_circle_by_two_points failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        circle3_id = response["result"]["data"]["entity_id"]
        radius = response["result"]["data"]["radius"]
        diameter = response["result"]["data"]["diameter"]
    else:
        circle3_id = response["result"]["entity_id"]
        radius = response["result"]["radius"]
        diameter = response["result"]["diameter"]
    logging.info(f"[PASS] create_circle_by_two_points: {circle3_id}")
    logging.info(f"  Radius: {radius}")
    logging.info(f"  Diameter: {diameter}")
    
    # Test 4: Test backward compatibility with original create_circle
    logging.info("Testing backward compatibility create_circle...")
    response = client.send_request("fusion.create_circle", {
        'sketch_id': sketch_id,
        'center': {'x': -20, 'y': 0},
        'radius': 3.0,
        'construction': False
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"create_circle (backward compatibility) failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        circle4_id = response["result"]["data"]["entity_id"]
        radius = response["result"]["data"]["radius"]
    else:
        circle4_id = response["result"]["entity_id"]
        radius = response["result"]["radius"]
    logging.info(f"[PASS] create_circle (backward compatibility): {circle4_id}")
    logging.info(f"  Radius: {radius}")
    
    return True, sketch_id, circle1_id, circle2_id, circle3_id, circle4_id

def test_circle_query_methods(client: CircleOperationsMCPClient, sketch_id: str, circle_id: str) -> bool:
    """Test circle query methods via MCP"""
    logging.info("Testing circle query methods...")
    
    # Test get_circle_properties
    logging.info("Testing get_circle_properties...")
    response = client.send_request("fusion.get_circle_properties", {
        'sketch_id': sketch_id,
        'circle_id': circle_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_circle_properties failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_circle_properties: {circle_id}")
    logging.info(f"  Radius: {data['radius']}")
    logging.info(f"  Area: {data['area']}")
    logging.info(f"  Circumference: {data['circumference']}")
    logging.info(f"  Center: ({data['center']['x']:.2f}, {data['center']['y']:.2f})")
    
    # Test get_circle_state
    logging.info("Testing get_circle_state...")
    response = client.send_request("fusion.get_circle_state", {
        'sketch_id': sketch_id,
        'circle_id': circle_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_circle_state failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_circle_state: {circle_id}")
    logging.info(f"  Construction: {data['is_construction']}")
    logging.info(f"  Deletable: {data['is_deletable']}")
    logging.info(f"  Fixed: {data['is_fixed']}")
    logging.info(f"  Visible: {data['is_visible']}")
    
    # Test get_circle_constraints
    logging.info("Testing get_circle_constraints...")
    response = client.send_request("fusion.get_circle_constraints", {
        'sketch_id': sketch_id,
        'circle_id': circle_id
    })
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_circle_constraints failed: {response}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_circle_constraints: {circle_id}")
    logging.info(f"  Constraints: {data['constraint_count']}")
    logging.info(f"  Dimensions: {data['dimension_count']}")
    
    return True

def test_circle_intersections(client: CircleOperationsMCPClient, sketch_id: str, circle_id: str) -> bool:
    """Test circle intersection methods via MCP"""
    logging.info("Testing circle intersection methods...")
    
    # Test get_circle_intersections
    logging.info("Testing get_circle_intersections...")
    logging.info(f"  Testing intersections for circle: {circle_id}")
    logging.info(f"  In sketch with other geometry present")
    
    response = client.send_request("fusion.get_circle_intersections", {
        'sketch_id': sketch_id,
        'circle_id': circle_id
    })
    
    # Debug: log the full response
    logging.info(f"get_circle_intersections response: {response}")
    
    if "error" in response or not response.get("result", {}).get("success"):
        logging.error(f"get_circle_intersections failed: {response}")
        logging.error(f"  Error details: {response.get('result', {}).get('error', 'Unknown error')}")
        return False
    
    # Handle different response structures
    if "data" in response["result"]:
        data = response["result"]["data"]
    else:
        data = response["result"]
    logging.info(f"[PASS] get_circle_intersections: {circle_id}")
    logging.info(f"  Intersections found: {data['intersection_count']}")
    
    # Log details of each intersection if any found
    if data['intersection_count'] > 0:
        for i, point in enumerate(data.get('intersection_points', [])):
            logging.info(f"  Intersection {i+1}: ({point['x']:.2f}, {point['y']:.2f})")
    else:
        logging.info(f"  No intersections found (this is normal for isolated circles)")
    
    return True

def run_simple_circle_test():
    """Run simple circle operations test via MCP"""
    start_time = datetime.now()
    logging.info("="*60)
    logging.info("STARTING SIMPLE CIRCLE OPERATIONS TEST VIA MCP")
    logging.info("="*60)
    
    client = CircleOperationsMCPClient()
    
    if not client.connect():
        logging.error("Failed to connect to MCP server")
        return False
    
    all_passed = True
    
    try:
        # Test circle creation methods
        result = test_circle_creation_methods(client)
        if not result:
            all_passed = False
        else:
            success, sketch_id, circle1_id, circle2_id, circle3_id, circle4_id = result
            logging.info("[PASS] Circle creation methods completed")
            
            # Test circle query methods
            if test_circle_query_methods(client, sketch_id, circle1_id):
                logging.info("[PASS] Circle query methods completed")
            else:
                all_passed = False
            
            # Test circle intersections
            if test_circle_intersections(client, sketch_id, circle1_id):
                logging.info("[PASS] Circle intersection methods completed")
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
        logging.info("Circle operations are working correctly via MCP!")
    else:
        logging.info("[FAIL] SOME MCP TESTS FAILED")
        logging.info("Check the log for details on what failed.")
    
    logging.info("")
    logging.info("TESTED METHODS VIA MCP:")
    tested_methods = [
        "create_circle_by_center_radius",
        "create_circle_by_three_points",
        "create_circle_by_two_points",
        "create_circle (backward compatibility)",
        "get_circle_properties", 
        "get_circle_constraints",
        "get_circle_state",
        "get_circle_intersections"
    ]
    
    for method in tested_methods:
        logging.info(f"  [TESTED] {method}")
    
    logging.info("")
    logging.info("NOTE: These tests called the real circle_operations.py methods")
    logging.info("through MCP socket communication with actual Fusion 360 API.")
    
    return all_passed

if __name__ == "__main__":
    success = run_simple_circle_test()
    exit(0 if success else 1)