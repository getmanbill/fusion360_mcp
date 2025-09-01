"""
Base utilities for sketch operations
Shared functions and validation to avoid code duplication
"""
import adsk.core
import adsk.fusion
from typing import Dict, Any, Optional, Tuple, List

class SketchBase:
    """Base class with common sketch utilities"""
    
    def __init__(self):
        self.app = adsk.core.Application.get()
        
    def get_active_design(self) -> Optional[adsk.fusion.Design]:
        """Get the active design, return None if not available"""
        design = self.app.activeProduct
        if not design or design.objectType != adsk.fusion.Design.classType():
            return None
        return design
    
    def get_sketch_by_id(self, sketch_id: str) -> Optional[adsk.fusion.Sketch]:
        """Get sketch by ID, return None if not found"""
        design = self.get_active_design()
        if not design:
            return None
            
        # Search through all components for the sketch
        all_sketches = []
        for comp in design.allComponents:
            all_sketches.extend(comp.sketches)
            
        for sketch in all_sketches:
            if sketch.entityToken == sketch_id or sketch.name == sketch_id:
                return sketch
        return None
    
    def validate_point(self, point: Dict[str, float]) -> Tuple[bool, str]:
        """Validate point coordinates"""
        if not isinstance(point, dict):
            return False, "Point must be an object"
        if 'x' not in point or 'y' not in point:
            return False, "Point must have 'x' and 'y' coordinates"
        try:
            float(point['x'])
            float(point['y'])
            return True, ""
        except (ValueError, TypeError):
            return False, "Point coordinates must be numeric"
    
    def create_point_2d(self, x: float, y: float) -> adsk.core.Point2D:
        """Create a 2D point"""
        return adsk.core.Point2D.create(x, y)
    
    def get_plane_by_reference(self, plane_ref: str) -> Optional[adsk.fusion.ConstructionPlane]:
        """Get construction plane by reference"""
        design = self.get_active_design()
        if not design:
            return None
            
        root_comp = design.rootComponent
        
        # Handle standard plane names
        if plane_ref.upper() == "XY":
            return root_comp.xYConstructionPlane
        elif plane_ref.upper() == "XZ":
            return root_comp.xZConstructionPlane
        elif plane_ref.upper() == "YZ":
            return root_comp.yZConstructionPlane
        
        # TODO: Handle face references and custom planes
        return None
    
    def error_response(self, message: str) -> Dict[str, Any]:
        """Standard error response format"""
        return {"error": message}
    
    def success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standard success response format"""
        return {"success": True, **data}
    
    def entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convert sketch entity to dictionary representation"""
        base_info = {
            "id": entity.entityToken,
            "type": entity.objectType,
            "is_construction": entity.isConstruction if hasattr(entity, 'isConstruction') else False
        }
        
        # Add type-specific information
        if hasattr(entity, 'startSketchPoint') and hasattr(entity, 'endSketchPoint'):
            # Line
            base_info.update({
                "start_point": {
                    "x": entity.startSketchPoint.geometry.x,
                    "y": entity.startSketchPoint.geometry.y
                },
                "end_point": {
                    "x": entity.endSketchPoint.geometry.x,
                    "y": entity.endSketchPoint.geometry.y
                }
            })
        elif hasattr(entity, 'centerSketchPoint') and hasattr(entity, 'radius'):
            # Circle/Arc
            base_info.update({
                "center": {
                    "x": entity.centerSketchPoint.geometry.x,
                    "y": entity.centerSketchPoint.geometry.y
                },
                "radius": entity.radius
            })
            
        return base_info
    
    def constraint_to_dict(self, constraint) -> Dict[str, Any]:
        """Convert constraint to dictionary representation"""
        return {
            "id": constraint.entityToken,
            "type": constraint.objectType,
            "is_driving": constraint.isDriving if hasattr(constraint, 'isDriving') else False
        }
    
    def wait_for_fusion_ready(self, max_iterations: int = 5) -> bool:
        """Wait for Fusion to complete pending operations using doEvents"""
        try:
            import adsk
            import time
            
            # Process pending events/messages with small delays
            for _ in range(max_iterations):
                adsk.doEvents()
                time.sleep(0.01)  # Small delay between doEvents calls
                
            return True
        except Exception as e:
            # Fallback to small delay if doEvents not available
            import time
            time.sleep(0.1)
            return False
    
    def ensure_design_computed(self) -> bool:
        """Ensure design is fully computed using computeAll"""
        try:
            design = self.get_active_design()
            if design:
                design.computeAll()
                return True
            return False
        except Exception as e:
            return False
    
    def wait_for_operation_complete(self, operation_name: str = "operation") -> bool:
        """Smart wait combining doEvents and computeAll"""
        try:
            # Step 1: Process pending UI events (reduced calls)
            self.wait_for_fusion_ready(3)
            
            # Step 2: Ensure design is computed  
            self.ensure_design_computed()
            
            # Step 3: Final doEvents cycle (minimal)
            self.wait_for_fusion_ready(2)
            
            return True
        except Exception as e:
            # Fallback to minimal delay
            import time
            time.sleep(0.2)
            return False
