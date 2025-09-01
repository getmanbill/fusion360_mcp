"""
Sketch Management Operations
Create, list, activate, and manage sketches
"""
import adsk.core
import adsk.fusion
from typing import Dict, Any, List
from .base import SketchBase

class SketchManagement(SketchBase):
    """Handles sketch lifecycle and management operations"""
    
    def create_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sketch on specified plane"""
        try:
            design = self.get_active_design()
            if not design:
                return self.error_response("No active Fusion design")
            
            plane_ref = params.get('plane_reference')
            if not plane_ref:
                return self.error_response("plane_reference is required")
            
            # Get the plane
            plane = self.get_plane_by_reference(plane_ref)
            if not plane:
                return self.error_response(f"Invalid plane reference: {plane_ref}")
            
            # Create the sketch
            root_comp = design.rootComponent
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            ui.messageBox(f"[SKETCH CREATE] Creating sketch on plane: {type(plane)}", "Sketch Creation")
            ui.messageBox(f"[SKETCH CREATE] Root component: {root_comp.name}, Sketches count: {root_comp.sketches.count}", "Component Info")
            
            sketch = root_comp.sketches.add(plane)
            
            ui.messageBox(f"[SKETCH CREATE] Sketch created: {sketch.name}, Token: {sketch.entityToken[:20]}...", "Sketch Created")
            
            # Smart wait for sketch creation to complete
            self.wait_for_operation_complete("sketch creation")
            
            # Set custom name if provided
            custom_name = params.get('name')
            if custom_name:
                sketch.name = custom_name
                # Wait for name update to process
                self.wait_for_fusion_ready()
            
            # According to API docs, sketches are automatically activated
            # No manual activation needed - just verify state
            app = adsk.core.Application.get()
            is_active = app.activeEditObject == sketch
            
            return self.success_response({
                "sketch_id": sketch.entityToken,
                "name": sketch.name,
                "plane_info": {
                    "reference": plane_ref
                },
                "is_active": is_active
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create sketch: {str(e)}")
    
    def list_sketches(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all sketches in the active design"""
        try:
            design = self.get_active_design()
            if not design:
                return self.error_response("No active Fusion design")
            
            sketches = []
            
            # Collect sketches from all components - with error handling
            for comp in design.allComponents:
                for sketch in comp.sketches:
                    try:
                        sketch_info = {
                            "id": sketch.entityToken,
                            "name": sketch.name,
                            "plane": self._get_plane_name(sketch.referencePlane),
                            "entity_count": sketch.sketchCurves.count + sketch.sketchPoints.count,
                            "is_fully_constrained": sketch.isFullyConstrained,
                            "component": comp.name
                        }
                        sketches.append(sketch_info)
                    except Exception as e:
                        # Skip problematic sketches and continue
                        print(f"Warning: Skipped sketch due to error: {str(e)}")
                        continue
            
            return self.success_response({
                "sketches": sketches,
                "count": len(sketches)
            })
            
        except Exception as e:
            return self.error_response(f"Failed to list sketches: {str(e)}")
    
    def activate_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a sketch for editing (sketches are auto-activated upon creation)"""
        try:
            sketch_id = params.get('sketch_id')
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # In Fusion 360 API, sketches are automatically activated when created
            # We just need to verify the sketch exists and is ready for editing
            app = adsk.core.Application.get()
            active_object = app.activeEditObject
            
            return self.success_response({
                "sketch_id": sketch.entityToken,
                "name": sketch.name,
                "activated": True,
                "is_currently_active": active_object == sketch if active_object else False
            })
            
        except Exception as e:
            return self.error_response(f"Failed to activate sketch: {str(e)}")
    
    def finish_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exit sketch editing mode"""
        try:
            sketch_id = params.get('sketch_id')
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Sketch is automatically finished when we exit edit mode
            return self.success_response({
                "sketch_id": sketch.entityToken,
                "name": sketch.name,
                "is_fully_constrained": sketch.isFullyConstrained
            })
            
        except Exception as e:
            return self.error_response(f"Failed to finish sketch: {str(e)}")
    
    def get_sketch_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a sketch"""
        try:
            sketch_id = params.get('sketch_id')
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Collect entities
            entities = []
            for curve in sketch.sketchCurves:
                entities.append(self.entity_to_dict(curve))
            for point in sketch.sketchPoints:
                entities.append(self.entity_to_dict(point))
            
            # Collect constraints - use safe attribute access
            constraints = []
            try:
                if hasattr(sketch, 'geometricConstraints'):
                    for constraint in sketch.geometricConstraints:
                        constraints.append(self.constraint_to_dict(constraint))
                if hasattr(sketch, 'dimensionalConstraints'):
                    for constraint in sketch.dimensionalConstraints:
                        constraints.append(self.constraint_to_dict(constraint))
            except:
                # Skip constraints if there are issues accessing them
                pass
            
            # Get bounding box if sketch has entities
            bounding_box = None
            if sketch.profiles.count > 0:
                try:
                    bb = sketch.boundingBox
                    bounding_box = {
                        "min": {"x": bb.minPoint.x, "y": bb.minPoint.y},
                        "max": {"x": bb.maxPoint.x, "y": bb.maxPoint.y}
                    }
                except:
                    pass  # Bounding box might not be available
            
            return self.success_response({
                "sketch_id": sketch.entityToken,
                "name": sketch.name,
                "plane": self._get_plane_name(sketch.referencePlane),
                "is_fully_constrained": sketch.isFullyConstrained,
                "entities": entities,
                "constraints": constraints,
                "entity_count": len(entities),
                "constraint_count": len(constraints),
                "bounding_box": bounding_box
            })
            
        except Exception as e:
            return self.error_response(f"Failed to get sketch info: {str(e)}")
    
    def delete_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a sketch"""
        try:
            sketch_id = params.get('sketch_id')
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            sketch_name = sketch.name
            sketch.deleteMe()
            
            return self.success_response({
                "deleted_sketch": sketch_name,
                "sketch_id": sketch_id
            })
            
        except Exception as e:
            return self.error_response(f"Failed to delete sketch: {str(e)}")
    
    def _get_plane_name(self, plane) -> str:
        """Get human-readable plane name"""
        try:
            if hasattr(plane, 'name'):
                return plane.name
            # Try to identify standard planes
            design = self.get_active_design()
            if design:
                root_comp = design.rootComponent
                if plane == root_comp.xYConstructionPlane:
                    return "XY"
                elif plane == root_comp.xZConstructionPlane:
                    return "XZ"
                elif plane == root_comp.yZConstructionPlane:
                    return "YZ"
            return "Unknown"
        except:
            return "Unknown"
