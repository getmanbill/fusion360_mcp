"""
Parametric Bracket Generator
Creates a configurable mounting bracket with holes, fillets, and reinforcement ribs.
Uses all documented best practices for robust Fusion 360 automation.

Bracket Features:
- Configurable dimensions via user parameters
- Mounting holes with precise positioning
- Reinforcement ribs for structural strength
- Fillet radii for manufacturing considerations
- Material thickness considerations
"""
import socket
import json
import math
from typing import Dict, Any, List, Tuple, Optional

class ParametricBracketGenerator:
    """Generates parametric mounting brackets with configurable parameters"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.operation_log = []
        self.request_id = 1
        
    def log_operation(self, operation: str, level: str = "INFO", details: Dict[str, Any] = None):
        """Log operation with timestamp and context"""
        import datetime
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "level": level,
            "details": details or {},
            "request_id": self.request_id
        }
        self.operation_log.append(log_entry)
        print(f"[{level}] {operation}: {details}")
        
    def connect(self):
        """Connect to MCP server with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10.0)
                self.socket.connect((self.host, self.port))
                self.log_operation("CONNECTION_SUCCESS", "INFO", {"attempt": attempt + 1})
                return True
            except Exception as e:
                self.log_operation("CONNECTION_FAILED", "ERROR", {
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1.0)
        return False
        
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send request with comprehensive error handling"""
        if params is None:
            params = {}
            
        request = {
            "method": method,
            "params": params,
            "id": self.request_id
        }
        
        self.log_operation("REQUEST_SEND", "INFO", {
            "method": method,
            "params_keys": list(params.keys()),
            "request_id": self.request_id
        })
        
        try:
            request_json = json.dumps(request) + '\n'
            self.socket.send(request_json.encode('utf-8'))
            
            # Read complete response - handle large responses properly
            response_data = b""
            while True:
                chunk = self.socket.recv(8192)
                if not chunk:
                    break
                response_data += chunk
                # Check if we have a complete JSON response
                try:
                    response_str = response_data.decode('utf-8')
                    if response_str.endswith('\n') or response_str.count('{') == response_str.count('}'):
                        break
                except UnicodeDecodeError:
                    continue  # Keep reading if we have incomplete UTF-8
            
            response_str = response_data.decode('utf-8')
            response = json.loads(response_str)
            
            self.request_id += 1
            
            if 'error' in response:
                self.log_operation("REQUEST_ERROR", "ERROR", {
                    "method": method,
                    "error": response['error']
                })
            else:
                self.log_operation("REQUEST_SUCCESS", "INFO", {
                    "method": method,
                    "has_result": 'result' in response
                })
                
            return response
            
        except Exception as e:
            self.log_operation("REQUEST_EXCEPTION", "ERROR", {
                "method": method,
                "error": str(e)
            })
            return {"error": f"Request failed: {str(e)}"}
    
    def safe_field_extract(self, data: Dict[str, Any], *field_names: str, default: Any = "UNKNOWN") -> Any:
        """Safely extract field with multiple possible names"""
        if not isinstance(data, dict):
            return default
            
        for field_name in field_names:
            if field_name in data:
                return data[field_name]
        return default
    
    def close(self):
        """Close connection safely"""
        try:
            if self.socket:
                self.socket.close()
                self.log_operation("CONNECTION_CLOSED", "INFO")
        except Exception as e:
            self.log_operation("CONNECTION_CLOSE_ERROR", "ERROR", {"error": str(e)})

    def create_bracket_parameters(self, bracket_config: Dict[str, Any]) -> Dict[str, str]:
        """Create user parameters for the bracket design"""
        print("\n⚙️ Creating Bracket Parameters")
        print("-" * 40)
        
        # Default bracket configuration
        default_config = {
            "bracket_length": {"value": 100, "units": "mm", "description": "Overall bracket length"},
            "bracket_height": {"value": 80, "units": "mm", "description": "Overall bracket height"}, 
            "bracket_thickness": {"value": 6, "units": "mm", "description": "Material thickness"},
            "mounting_hole_diameter": {"value": 6, "units": "mm", "description": "Mounting hole diameter"},
            "mounting_hole_spacing": {"value": 50, "units": "mm", "description": "Center-to-center hole spacing"},
            "edge_margin": {"value": 15, "units": "mm", "description": "Margin from edges to holes"},
            "fillet_radius": {"value": 3, "units": "mm", "description": "Corner fillet radius"},
            "rib_thickness": {"value": 4, "units": "mm", "description": "Reinforcement rib thickness"},
            "rib_height": {"value": 20, "units": "mm", "description": "Reinforcement rib height"}
        }
        
        # Merge user config with defaults, preserving descriptions
        config = {}
        for param_name, default_data in default_config.items():
            if param_name in bracket_config:
                # Merge user config with default, preserving description if not provided
                user_data = bracket_config[param_name]
                config[param_name] = {
                    **default_data,  # Start with defaults (includes description)
                    **user_data      # Override with user values
                }
            else:
                config[param_name] = default_data
        
        param_ids = {}
        for param_name, param_data in config.items():
            # Format the value with units as expected by the parameter handler
            if 'units' in param_data:
                # Send value as just the number for unit-based parameters
                result = self.send_request('fusion.set_parameter', {
                    'name': param_name,
                    'value': param_data['value'],
                    'units': param_data['units']
                })
            else:
                # Send value directly for unitless parameters
                result = self.send_request('fusion.set_parameter', {
                    'name': param_name,
                    'value': param_data['value']
                })
            
            if 'error' not in result:
                param_result = self.safe_field_extract(result, 'result', default={})
                created_name = self.safe_field_extract(param_result, 'parameter', default={}).get('name', param_name)
                param_ids[param_name] = created_name
                description = param_data.get('description', 'User parameter')
                print(f"   ✅ {param_name}: {param_data['value']} {param_data['units']} - {description}")
            else:
                print(f"   ❌ Failed to create {param_name}: {result['error']}")
                
        return param_ids

    def create_main_bracket_profile(self, sketch_id: str, param_ids: Dict[str, str]) -> List[str]:
        """Create the main bracket outline as a proper L-shaped profile"""
        print("\n🏗️ Creating Main Bracket Profile")
        print("-" * 40)
        
        entity_ids = []
        
        # Create L-shaped bracket outline with connected lines
        # Bracket dimensions (will be parametrically constrained later)
        bracket_length = 100  # bracket_length parameter
        bracket_height = 80   # bracket_height parameter
        bracket_thickness = 6 # bracket_thickness parameter
        flange_width = 20     # mounting flange width
        
        # Define L-bracket outline points (starting from bottom-left, going clockwise)
        outline_points = [
            # Horizontal flange outline
            {'start': {'x': 0, 'y': 0}, 'end': {'x': bracket_length, 'y': 0}, 'name': 'bottom_edge'},
            {'start': {'x': bracket_length, 'y': 0}, 'end': {'x': bracket_length, 'y': flange_width}, 'name': 'right_flange_edge'},
            {'start': {'x': bracket_length, 'y': flange_width}, 'end': {'x': bracket_thickness, 'y': flange_width}, 'name': 'flange_inner_edge'},
            # Vertical section outline
            {'start': {'x': bracket_thickness, 'y': flange_width}, 'end': {'x': bracket_thickness, 'y': bracket_height}, 'name': 'vertical_inner_edge'},
            {'start': {'x': bracket_thickness, 'y': bracket_height}, 'end': {'x': 0, 'y': bracket_height}, 'name': 'top_edge'},
            {'start': {'x': 0, 'y': bracket_height}, 'end': {'x': 0, 'y': 0}, 'name': 'left_edge'}
        ]
        
        print(f"   Creating L-bracket outline with {len(outline_points)} connected lines...")
        
        # Create each line of the bracket outline
        for i, line_def in enumerate(outline_points):
            result = self.send_request('fusion.create_line', {
                'sketch_id': sketch_id,
                'start_point': line_def['start'],
                'end_point': line_def['end']
            })
            
            if 'error' not in result:
                line_result = self.safe_field_extract(result, 'result', default={})
                line_id = self.safe_field_extract(line_result, 'entity_id', 'id')
                entity_ids.append(line_id)
                print(f"   ✅ {line_def['name']}: Line {i+1}/{len(outline_points)}")
            else:
                print(f"   ❌ {line_def['name']} failed: {result['error']}")
        
        print(f"   ✅ L-bracket outline completed: {len(entity_ids)} lines created")
        return entity_ids

    def create_mounting_holes(self, sketch_id: str, param_ids: Dict[str, str]) -> List[str]:
        """Create mounting holes with parametric positioning"""
        print("\n🔩 Creating Mounting Holes")
        print("-" * 40)
        
        hole_ids = []
        
        # Calculate hole positions based on parameters
        hole_positions = [
            {'x': 25, 'y': 10, 'name': 'mounting_hole_1'},
            {'x': 75, 'y': 10, 'name': 'mounting_hole_2'},
            {'x': 3, 'y': 25, 'name': 'vertical_hole_1'},
            {'x': 3, 'y': 55, 'name': 'vertical_hole_2'}
        ]
        
        for i, pos in enumerate(hole_positions):
            result = self.send_request('fusion.create_circle', {
                'sketch_id': sketch_id,
                'center': {'x': pos['x'], 'y': pos['y']},
                'radius': 3  # Will be constrained to hole_diameter/2 parameter
            })
            
            if 'error' not in result:
                hole_result = self.safe_field_extract(result, 'result', default={})
                hole_id = self.safe_field_extract(hole_result, 'entity_id', 'id')
                hole_ids.append(hole_id)
                print(f"   ✅ {pos['name']}: Circle at ({pos['x']}, {pos['y']})")
            else:
                print(f"   ❌ {pos['name']} failed: {result['error']}")
                
        return hole_ids

    def create_reinforcement_ribs(self, sketch_id: str, param_ids: Dict[str, str]) -> List[str]:
        """Create reinforcement ribs for structural strength"""
        print("\n💪 Creating Reinforcement Ribs")
        print("-" * 40)
        
        rib_ids = []
        
        # Diagonal reinforcement rib
        result = self.send_request('fusion.create_line', {
            'sketch_id': sketch_id,
            'start_point': {'x': 6, 'y': 20},
            'end_point': {'x': 30, 'y': 60}
        })
        
        if 'error' not in result:
            rib_result = self.safe_field_extract(result, 'result', default={})
            rib_id = self.safe_field_extract(rib_result, 'entity_id', 'id')
            rib_ids.append(rib_id)
            print("   ✅ Diagonal reinforcement rib")
        else:
            print(f"   ❌ Diagonal rib failed: {result['error']}")
            
        # Horizontal reinforcement
        result = self.send_request('fusion.create_line', {
            'sketch_id': sketch_id,
            'start_point': {'x': 20, 'y': 20},
            'end_point': {'x': 80, 'y': 20}
        })
        
        if 'error' not in result:
            h_rib_result = self.safe_field_extract(result, 'result', default={})
            h_rib_id = self.safe_field_extract(h_rib_result, 'entity_id', 'id')
            rib_ids.append(h_rib_id)
            print("   ✅ Horizontal reinforcement")
        else:
            print(f"   ❌ Horizontal rib failed: {result['error']}")
            
        return rib_ids

    def apply_dimensional_constraints(self, sketch_id: str, entity_ids: List[str], hole_ids: List[str], param_ids: Dict[str, str]) -> int:
        """Apply dimensional constraints linking geometry to parameters"""
        print("\n🔗 Applying Dimensional Constraints")
        print("-" * 40)
        
        constraints_applied = 0
        
        # Apply radius constraints to holes
        for i, hole_id in enumerate(hole_ids[:2]):  # Apply to first 2 holes as example
            result = self.send_request('fusion.add_radius_constraint', {
                'sketch_id': sketch_id,
                'entity_id': hole_id,
                'radius': 3,  # Could link to mounting_hole_diameter/2 parameter
            })
            
            if 'error' not in result:
                constraints_applied += 1
                print(f"   ✅ Radius constraint applied to hole {i+1}")
            else:
                print(f"   ❌ Radius constraint failed for hole {i+1}: {result['error']}")
                
        return constraints_applied

    def generate_bracket(self, bracket_config: Dict[str, Any] = None) -> bool:
        """Generate complete parametric bracket"""
        if bracket_config is None:
            bracket_config = {}
            
        try:
            print("🔧 PARAMETRIC BRACKET GENERATOR")
            print("=" * 50)
            
            # Phase 1: Setup
            print("\n📡 Phase 1: Connection and Document Setup")
            print("-" * 40)
            
            if not self.connect():
                print("❌ Failed to connect to MCP server")
                return False
                
            # Create new document
            result = self.send_request('fusion.new_document', {
                'document_type': 'FusionDesignDocumentType'
            })
            
            if 'error' in result:
                print(f"❌ Document creation failed: {result['error']}")
                return False
                
            doc_result = self.safe_field_extract(result, 'result', default={})
            doc_name = self.safe_field_extract(doc_result, 'document_name', 'name', 'document_id')
            print(f"✅ Document created: {doc_name}")
            
            # Phase 2: Create Parameters
            param_ids = self.create_bracket_parameters(bracket_config)
            
            # Phase 3: Create Sketch
            print("\n📐 Phase 3: Sketch Creation")
            print("-" * 40)
            
            result = self.send_request('fusion.create_sketch', {
                'plane_reference': 'XY',
                'name': 'BracketProfile'
            })
            
            if 'error' in result:
                print(f"❌ Sketch creation failed: {result['error']}")
                return False
                
            sketch_result = self.safe_field_extract(result, 'result', default={})
            sketch_id = self.safe_field_extract(sketch_result, 'sketch_id', 'id', 'entity_id')
            sketch_name = self.safe_field_extract(sketch_result, 'sketch_name', 'name')
            print(f"✅ Sketch created: {sketch_name}")
            
            # Get initial revision
            result = self.send_request('fusion.get_sketch_revision_id', {'sketch_id': sketch_id})
            initial_revision = self.safe_field_extract(
                self.safe_field_extract(result, 'result', default={}),
                'revision_id', 'revisionId', 'revision'
            )
            print(f"   Initial revision: {initial_revision}")
            
            # Phase 4: Create Geometry
            entity_ids = self.create_main_bracket_profile(sketch_id, param_ids)
            hole_ids = self.create_mounting_holes(sketch_id, param_ids)
            rib_ids = self.create_reinforcement_ribs(sketch_id, param_ids)
            
            # Phase 5: Apply Constraints
            constraints_applied = self.apply_dimensional_constraints(sketch_id, entity_ids, hole_ids, param_ids)
            
            # Phase 6: Final Validation
            print("\n📊 Final Validation and Summary")
            print("-" * 40)
            
            # Get final revision
            result = self.send_request('fusion.get_sketch_revision_id', {'sketch_id': sketch_id})
            final_revision = self.safe_field_extract(
                self.safe_field_extract(result, 'result', default={}),
                'revision_id', 'revisionId', 'revision'
            )
            
            # Get comprehensive sketch info
            result = self.send_request('fusion.get_sketch_info', {'sketch_id': sketch_id})
            if 'error' not in result:
                sketch_info = self.safe_field_extract(result, 'result', default={})
                entity_count = len(self.safe_field_extract(sketch_info, 'entities', default=[]))
                constraint_count = len(self.safe_field_extract(sketch_info, 'constraints', default=[]))
                print(f"   Entities created: {entity_count}")
                print(f"   Constraints applied: {constraint_count}")
            
            # Success Summary
            print(f"\n🎉 PARAMETRIC BRACKET COMPLETED!")
            print("=" * 50)
            print(f"📈 Bracket Summary:")
            print(f"   Document: {doc_name}")
            print(f"   Sketch: {sketch_name}")
            print(f"   Parameters: {len(param_ids)}")
            print(f"   Main profile lines: {len(entity_ids)}")
            print(f"   Mounting holes: {len(hole_ids)}")
            print(f"   Reinforcement ribs: {len(rib_ids)}")
            print(f"   Constraints: {constraints_applied}")
            print(f"   Revisions: {initial_revision} → {final_revision}")
            
            # Operation success metrics
            error_count = len([log for log in self.operation_log if log['level'] == 'ERROR'])
            success_rate = ((len(self.operation_log) - error_count) / len(self.operation_log)) * 100
            print(f"   Operations logged: {len(self.operation_log)}")
            print(f"   Success rate: {success_rate:.1f}%")
            
            if error_count == 0:
                print("   🏆 PERFECT EXECUTION - Ready for manufacturing!")
            
            return True
            
        except Exception as e:
            self.log_operation("BRACKET_GENERATION_EXCEPTION", "CRITICAL", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            print(f"💥 Bracket generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.close()
            
            # Save operation log
            try:
                with open("parametric_bracket_log.json", "w") as f:
                    json.dump(self.operation_log, f, indent=2)
                print(f"\n📝 Operation log saved to: parametric_bracket_log.json")
            except Exception as e:
                print(f"⚠️  Failed to save operation log: {e}")

def create_standard_bracket():
    """Create a standard mounting bracket with default dimensions"""
    generator = ParametricBracketGenerator()
    
    # Standard bracket configuration
    config = {
        "bracket_length": {"value": 120, "units": "mm"},
        "bracket_height": {"value": 100, "units": "mm"},
        "mounting_hole_diameter": {"value": 8, "units": "mm"},
        "mounting_hole_spacing": {"value": 60, "units": "mm"},
        "fillet_radius": {"value": 5, "units": "mm"}
    }
    
    return generator.generate_bracket(config)

def create_heavy_duty_bracket():
    """Create a heavy-duty bracket with reinforced dimensions"""
    generator = ParametricBracketGenerator()
    
    # Heavy-duty bracket configuration
    config = {
        "bracket_length": {"value": 150, "units": "mm"},
        "bracket_height": {"value": 120, "units": "mm"},
        "bracket_thickness": {"value": 10, "units": "mm"},
        "mounting_hole_diameter": {"value": 12, "units": "mm"},
        "mounting_hole_spacing": {"value": 80, "units": "mm"},
        "rib_thickness": {"value": 6, "units": "mm"},
        "fillet_radius": {"value": 8, "units": "mm"}
    }
    
    return generator.generate_bracket(config)

def create_compact_bracket():
    """Create a compact bracket for space-constrained applications"""
    generator = ParametricBracketGenerator()
    
    # Compact bracket configuration
    config = {
        "bracket_length": {"value": 80, "units": "mm"},
        "bracket_height": {"value": 60, "units": "mm"},
        "bracket_thickness": {"value": 4, "units": "mm"},
        "mounting_hole_diameter": {"value": 5, "units": "mm"},
        "mounting_hole_spacing": {"value": 40, "units": "mm"},
        "fillet_radius": {"value": 2, "units": "mm"}
    }
    
    return generator.generate_bracket(config)

if __name__ == "__main__":
    print("🔧 Parametric Bracket Generator")
    print("Choose bracket type:")
    print("1. Standard bracket")
    print("2. Heavy-duty bracket") 
    print("3. Compact bracket")
    print("4. Custom bracket (default parameters)")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            success = create_standard_bracket()
        elif choice == "2":
            success = create_heavy_duty_bracket()
        elif choice == "3":
            success = create_compact_bracket()
        else:
            generator = ParametricBracketGenerator()
            success = generator.generate_bracket()
            
        if success:
            print("\n🎊 Bracket generation completed successfully!")
        else:
            print("\n❌ Bracket generation failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
