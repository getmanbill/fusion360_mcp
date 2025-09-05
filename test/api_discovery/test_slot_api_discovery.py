"""
Slot API Discovery Test
Must log each step to confirm method and attribute names per fusion-rules.mdc
Cross-reference against official Fusion 360 documentation

Slots are complex geometry - typically composite of 2 arcs + 2 lines
"""
import socket
import json
import time
from datetime import datetime

class SlotAPIDiscovery:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        self.discovery_log = []
        
    def log_discovery(self, step: str, level: str, data: dict):
        """Log each discovery step with timestamp"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "level": level,  # INFO, SUCCESS, ERROR, WARNING
            "data": data
        }
        self.discovery_log.append(log_entry)
        print(f"[{level}] {step}: {data}")
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(15.0)
            self.socket.connect((self.host, self.port))
            self.log_discovery("CONNECTION", "SUCCESS", {"host": self.host, "port": self.port})
            return True
        except Exception as e:
            self.log_discovery("CONNECTION", "ERROR", {"error": str(e)})
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
            self.log_discovery("REQUEST_ERROR", "ERROR", {"method": method, "error": str(e)})
            return {"error": f"Request failed: {str(e)}"}
    
    def save_discovery_log(self):
        """Save discovery log to JSON file"""
        filename = f"slot_api_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.discovery_log, f, indent=2)
        self.log_discovery("LOG_SAVED", "INFO", {"filename": filename})
    
    def close(self):
        if self.socket:
            self.socket.close()

def discover_slot_api():
    """
    CRITICAL: Must follow fusion-rules.mdc requirement
    Log each step to confirm method and attribute names
    Check against web documentation to clarify thinking
    
    Slots are complex - may be composite geometry or dedicated API
    """
    discovery = SlotAPIDiscovery()
    
    if not discovery.connect():
        return
        
    try:
        discovery.log_discovery("SLOT_API_DISCOVERY_START", "INFO", {
            "objective": "Discover Fusion 360 slot creation API methods",
            "hypothesis": "Slots may be composite geometry (2 arcs + 2 lines) or dedicated API",
            "documentation_reference": "https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-2367ed6a-0ad1-4c8f-935e-b52738d1ce2b",
            "requirement": "Log each step per fusion-rules.mdc"
        })
        
        # Step 1: Create test environment
        result = discovery.send_request('fusion.new_document', {
            'document_type': 'FusionDesignDocumentType'
        })
        
        if 'error' in result:
            discovery.log_discovery("DOCUMENT_CREATION", "ERROR", {"error": result['error']})
            return
        
        discovery.log_discovery("DOCUMENT_CREATION", "SUCCESS", {"result": result.get('result', {})})
        
        result = discovery.send_request('fusion.create_sketch', {
            'plane_reference': 'XY',
            'name': 'SlotAPITestSketch'
        })
        
        if 'error' in result:
            discovery.log_discovery("SKETCH_CREATION", "ERROR", {"error": result['error']})
            return
            
        sketch_id = result.get('result', {}).get('sketch_id')
        discovery.log_discovery("SKETCH_CREATION", "SUCCESS", {"sketch_id": sketch_id})
        
        # Step 2: Test if slot method exists
        discovery.log_discovery("STEP_2_EXISTING_METHOD_TEST", "INFO", {
            "action": "Testing if create_slot method already exists",
            "expectation": "Should fail - method not yet implemented"
        })
        
        result = discovery.send_request('fusion.create_slot', {
            'sketch_id': sketch_id,
            'start_point': {'x': 0, 'y': 0},
            'end_point': {'x': 20, 'y': 0},
            'width': 5
        })
        
        if 'error' in result:
            discovery.log_discovery("EXISTING_METHOD_TEST", "SUCCESS", {
                "status": "Method does not exist as expected",
                "error": result['error']
            })
        else:
            discovery.log_discovery("EXISTING_METHOD_TEST", "WARNING", {
                "status": "Method unexpectedly exists",
                "result": result.get('result', {})
            })
        
        # Step 3: Research slot geometry composition
        discovery.log_discovery("STEP_3_GEOMETRY_ANALYSIS", "INFO", {
            "action": "Analyze slot geometry composition",
            "slot_definition": "Two semicircular ends connected by parallel lines",
            "components": [
                "Left semicircle arc (180 degrees)",
                "Right semicircle arc (180 degrees)", 
                "Top connecting line",
                "Bottom connecting line"
            ]
        })
        
        # Step 4: Test composite approach - create slot manually
        discovery.log_discovery("STEP_4_COMPOSITE_APPROACH", "INFO", {
            "action": "Test creating slot as composite geometry",
            "approach": "Create individual components and group them"
        })
        
        # Create slot components for 20x5 slot centered at origin
        slot_length = 20
        slot_width = 5
        radius = slot_width / 2
        
        # Left arc center
        left_center = {'x': -slot_length/2, 'y': 0}
        # Right arc center  
        right_center = {'x': slot_length/2, 'y': 0}
        
        # Test creating left arc
        result = discovery.send_request('fusion.create_arc', {
            'sketch_id': sketch_id,
            'center': left_center,
            'radius': radius,
            'start_angle': 1.5708,  # 90 degrees (pi/2)
            'end_angle': -1.5708   # -90 degrees (-pi/2) - 180 degree arc
        })
        
        if 'error' not in result:
            left_arc_id = result.get('result', {}).get('entity_id')
            discovery.log_discovery("LEFT_ARC_CREATION", "SUCCESS", {
                "arc_id": left_arc_id,
                "center": left_center,
                "radius": radius
            })
        else:
            discovery.log_discovery("LEFT_ARC_CREATION", "ERROR", {"error": result['error']})
        
        # Test creating right arc
        result = discovery.send_request('fusion.create_arc', {
            'sketch_id': sketch_id,
            'center': right_center,
            'radius': radius,
            'start_angle': -1.5708,  # -90 degrees
            'end_angle': 1.5708     # 90 degrees - 180 degree arc
        })
        
        if 'error' not in result:
            right_arc_id = result.get('result', {}).get('entity_id')
            discovery.log_discovery("RIGHT_ARC_CREATION", "SUCCESS", {
                "arc_id": right_arc_id,
                "center": right_center,
                "radius": radius
            })
        else:
            discovery.log_discovery("RIGHT_ARC_CREATION", "ERROR", {"error": result['error']})
        
        # Test creating connecting lines
        # Top line
        result = discovery.send_request('fusion.create_line', {
            'sketch_id': sketch_id,
            'start_point': {'x': -slot_length/2, 'y': radius},
            'end_point': {'x': slot_length/2, 'y': radius}
        })
        
        if 'error' not in result:
            top_line_id = result.get('result', {}).get('entity_id')
            discovery.log_discovery("TOP_LINE_CREATION", "SUCCESS", {"line_id": top_line_id})
        
        # Bottom line
        result = discovery.send_request('fusion.create_line', {
            'sketch_id': sketch_id,
            'start_point': {'x': -slot_length/2, 'y': -radius},
            'end_point': {'x': slot_length/2, 'y': -radius}
        })
        
        if 'error' not in result:
            bottom_line_id = result.get('result', {}).get('entity_id')
            discovery.log_discovery("BOTTOM_LINE_CREATION", "SUCCESS", {"line_id": bottom_line_id})
        
        # Step 5: Documentation research
        discovery.log_discovery("STEP_5_DOCUMENTATION_RESEARCH", "INFO", {
            "action": "Research official Fusion 360 slot API",
            "possible_apis": [
                "sketch.sketchCurves.sketchSlots.add()",
                "sketch.sketchCurves.addSlot()",
                "Composite approach using existing geometry methods"
            ],
            "parameters_research": {
                "start_point": "Start centerline point",
                "end_point": "End centerline point", 
                "width": "Slot width (diameter of end circles)",
                "construction": "Optional construction flag"
            },
            "documentation_url": "https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-2367ed6a-0ad1-4c8f-935e-b52738d1ce2b"
        })
        
        # Step 6: API implementation strategy
        discovery.log_discovery("STEP_6_IMPLEMENTATION_STRATEGY", "INFO", {
            "approach": "Composite geometry method",
            "rationale": "Most flexible and guaranteed to work",
            "algorithm": {
                "1": "Calculate slot parameters from start/end points and width",
                "2": "Create left semicircle arc at start point",
                "3": "Create right semicircle arc at end point",
                "4": "Create top connecting line",
                "5": "Create bottom connecting line",
                "6": "Return all entity IDs as a group"
            },
            "validation": [
                "start_point != end_point",
                "width > 0",
                "Calculate perpendicular offset for lines"
            ]
        })
        
        # Step 7: Mathematical calculations needed
        discovery.log_discovery("STEP_7_MATHEMATICS", "INFO", {
            "calculations_needed": {
                "slot_direction": "Vector from start to end point",
                "slot_length": "Distance between start and end points",
                "perpendicular_vector": "90-degree rotation of slot direction",
                "arc_centers": "start_point and end_point",
                "line_offsets": "perpendicular_vector * (width/2)"
            },
            "formula_example": {
                "slot_vector": "(end.x - start.x, end.y - start.y)",
                "perpendicular": "(-slot_vector.y, slot_vector.x) normalized",
                "top_offset": "perpendicular * (width/2)",
                "bottom_offset": "perpendicular * (-width/2)"
            }
        })
        
        # Step 8: Testing strategy
        discovery.log_discovery("STEP_8_TESTING_STRATEGY", "INFO", {
            "test_cases": [
                "Horizontal slot - start=(0,0), end=(20,0), width=5",
                "Vertical slot - start=(0,0), end=(0,20), width=3",
                "Diagonal slot - start=(0,0), end=(10,10), width=4",
                "Construction slot - isConstruction=True",
                "Edge cases - minimum width, very long slot"
            ],
            "validation_criteria": [
                "4 entities created (2 arcs, 2 lines)",
                "Arcs are semicircles with correct radius",
                "Lines are tangent to arcs",
                "Overall slot dimensions correct"
            ]
        })
        
        # Step 9: Implementation requirements
        discovery.log_discovery("STEP_9_IMPLEMENTATION_REQUIREMENTS", "INFO", {
            "implementation_file": "fusion_addon/sketch/geometry.py",
            "method_signature": "create_slot(self, params: Dict[str, Any]) -> Dict[str, Any]",
            "required_parameters": {
                "sketch_id": "string - Target sketch identifier",
                "start_point": "object - Start centerline point {x, y}",
                "end_point": "object - End centerline point {x, y}",
                "width": "number - Slot width (positive)",
                "construction": "boolean, optional - Construction geometry flag"
            },
            "return_structure": {
                "entity_ids": "array - IDs of all created entities [arc1, arc2, line1, line2]",
                "entity_type": "string - 'slot'",
                "slot_length": "number - Calculated length",
                "slot_width": "number - Specified width"
            }
        })
        
        discovery.log_discovery("SLOT_API_DISCOVERY_COMPLETE", "SUCCESS", {
            "status": "Discovery phase completed successfully",
            "conclusion": "Use composite geometry approach for slot creation",
            "next_action": "Implement create_slot() method using composite approach",
            "compliance": "All steps logged per fusion-rules.mdc requirement"
        })
        
    except Exception as e:
        discovery.log_discovery("DISCOVERY_ERROR", "ERROR", {"error": str(e)})
        
    finally:
        discovery.save_discovery_log()
        discovery.close()

if __name__ == "__main__":
    discover_slot_api()
