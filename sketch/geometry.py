"""
Basic Geometry Creation
Rectangle, circle, line, arc creation operations
"""
import adsk.core
import adsk.fusion
import math
from typing import Dict, Any, List
from .base import SketchBase

class SketchGeometry(SketchBase):
    """Handles basic sketch geometry creation"""
    
    def create_rectangle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rectangle from two corner points"""
        try:
            sketch_id = params.get('sketch_id')
            corner1 = params.get('corner1')
            corner2 = params.get('corner2')
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            valid1, msg1 = self.validate_point(corner1)
            if not valid1:
                return self.error_response(f"Invalid corner1: {msg1}")
            
            valid2, msg2 = self.validate_point(corner2)
            if not valid2:
                return self.error_response(f"Invalid corner2: {msg2}")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Ensure sketch is active and in edit mode
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            # Critical: Must ensure sketch is properly in edit mode
            if app.activeEditObject != sketch:
                try:
                    # Method 1: Use sketch.edit() - this should put sketch in edit mode
                    sketch.edit()
                    # Give Fusion time to enter edit mode
                    self.wait_for_operation_complete("sketch activation")
                except:
                    # Method 2: Try using the UI command if edit() fails
                    try:
                        ui.activeSelections.clear()
                        ui.activeSelections.add(sketch)
                        edit_cmd = ui.commandDefinitions.itemById('SketchActivate')
                        if edit_cmd:
                            edit_cmd.execute()
                            self.wait_for_operation_complete("sketch activation via command")
                    except:
                        pass  # Continue anyway
            
            # Double-check sketch is now active
            if app.activeEditObject != sketch:
                return self.error_response("Failed to activate sketch for editing")
            
            # Use official API documentation pattern: Point3D.create(x, y, 0)
            # This fixes the InternalValidationError: getAcGePoint3D issue
            try:
                point1 = adsk.core.Point3D.create(corner1['x'], corner1['y'], 0)
                point2 = adsk.core.Point3D.create(corner2['x'], corner2['y'], 0)
                
                # Validate points are different
                if abs(point1.x - point2.x) < 0.001 and abs(point1.y - point2.y) < 0.001:
                    return self.error_response("Rectangle corners are too close together")
                
            except Exception as pt_error:
                return self.error_response(f"Failed to create Point3D objects: {str(pt_error)}")
            
            # Create rectangle using official API pattern - should work reliably
            try:
                rect_lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point1, point2)
                if not rect_lines or len(rect_lines) == 0:
                    return self.error_response("Rectangle creation returned no lines")
                
                # Smart wait for operation completion instead of arbitrary delay
                self.wait_for_operation_complete("rectangle creation")
                    
            except Exception as rect_error:
                return self.error_response(f"Rectangle creation failed with Point3D: {str(rect_error)}")
            
            # Set construction mode if requested
            entity_ids = []
            for line in rect_lines:
                if construction:
                    line.isConstruction = True
                entity_ids.append(line.entityToken)
            
            # Ensure geometry is processed before getting constraints
            self.wait_for_fusion_ready()
            
            # Get auto-applied constraints
            constraints = []
            for constraint in sketch.geometricConstraints:
                constraints.append(self.constraint_to_dict(constraint))
            
            return self.success_response({
                "entity_ids": entity_ids,
                "entity_type": "rectangle",
                "construction": construction,
                "constraints": constraints[-4:] if len(constraints) >= 4 else constraints  # Last 4 are likely the rectangle constraints
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create rectangle: {str(e)}")
    
    def create_circle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a circle"""
        try:
            sketch_id = params.get('sketch_id')
            center = params.get('center')
            radius = params.get('radius')
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            valid_center, msg = self.validate_point(center)
            if not valid_center:
                return self.error_response(f"Invalid center: {msg}")
            
            if not isinstance(radius, (int, float)) or radius <= 0:
                return self.error_response("radius must be a positive number")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Create circle using Point3D for consistency with API docs
            center_pt = adsk.core.Point3D.create(center['x'], center['y'], 0)
            circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center_pt, radius)
            
            if construction:
                circle.isConstruction = True
            
            return self.success_response({
                "entity_id": circle.entityToken,
                "center_point_id": circle.centerSketchPoint.entityToken,
                "entity_type": "circle",
                "radius": radius,
                "construction": construction
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create circle: {str(e)}")
    
    def create_line(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a line between two points"""
        try:
            sketch_id = params.get('sketch_id')
            start_point = params.get('start_point')
            end_point = params.get('end_point')
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            valid_start, msg1 = self.validate_point(start_point)
            if not valid_start:
                return self.error_response(f"Invalid start_point: {msg1}")
            
            valid_end, msg2 = self.validate_point(end_point)
            if not valid_end:
                return self.error_response(f"Invalid end_point: {msg2}")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # MCP-safe creator based on research
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            # 1) Ensure Design workspace + product
            ui.workspaces.itemById('FusionSolidEnvironment').activate()
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                return self.error_response("Active product is not a Design")
            
            # 2) Reacquire sketch from token (avoids stale refs)
            sketch = adsk.fusion.Sketch.cast(design.findEntityByToken(sketch_id)[0])
            
            # 3) Normalize proxy & activate occurrence
            if sketch.assemblyContext:
                sketch.assemblyContext.activate()
                sketch = adsk.fusion.Sketch.cast(sketch.nativeObject)
            
            # 4) Force document regeneration
            design.computeAll()
            
            # Verify points are different
            if abs(start_point['x'] - end_point['x']) < 0.001 and abs(start_point['y'] - end_point['y']) < 0.001:
                return self.error_response("Line start and end points are too close together")
            
            # 5) Convert to sketch space & create geometry
            try:
                p1 = sketch.modelToSketchSpace(adsk.core.Point3D.create(
                    float(start_point['x']), 
                    float(start_point['y']), 
                    0.0
                ))
                p2 = sketch.modelToSketchSpace(adsk.core.Point3D.create(
                    float(end_point['x']), 
                    float(end_point['y']), 
                    0.0
                ))
                
                line = sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
                
                if not line:
                    return self.error_response("Line creation returned null")
                
                # Set properties
                if construction:
                    line.isConstruction = True
                
                # Wait for operation to complete
                self.wait_for_operation_complete("line creation")
                
                return self.success_response({
                    "entity_id": line.entityToken,
                    "start_point_id": line.startSketchPoint.entityToken,
                    "end_point_id": line.endSketchPoint.entityToken,
                    "entity_type": "line",
                    "construction": construction
                })
                
            except Exception as line_error:
                return self.error_response(f"Line creation failed: {str(line_error)}")
            
        except Exception as e:
            return self.error_response(f"Failed to create line: {str(e)}")
    
    def create_arc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an arc by center, start angle, and end angle"""
        try:
            sketch_id = params.get('sketch_id')
            center = params.get('center')
            radius = params.get('radius')
            start_angle = params.get('start_angle')
            end_angle = params.get('end_angle')
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            valid_center, msg = self.validate_point(center)
            if not valid_center:
                return self.error_response(f"Invalid center: {msg}")
            
            if not isinstance(radius, (int, float)) or radius <= 0:
                return self.error_response("radius must be a positive number")
            
            if not isinstance(start_angle, (int, float)):
                return self.error_response("start_angle must be a number (radians)")
            
            if not isinstance(end_angle, (int, float)):
                return self.error_response("end_angle must be a number (radians)")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Calculate start and end points
            center_pt = self.create_point_2d(center['x'], center['y'])
            start_x = center['x'] + radius * math.cos(start_angle)
            start_y = center['y'] + radius * math.sin(start_angle)
            end_x = center['x'] + radius * math.cos(end_angle)
            end_y = center['y'] + radius * math.sin(end_angle)
            
            start_pt = self.create_point_2d(start_x, start_y)
            end_pt = self.create_point_2d(end_x, end_y)
            
            # Create arc
            arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(center_pt, start_pt, end_pt)
            
            if construction:
                arc.isConstruction = True
            
            return self.success_response({
                "entity_id": arc.entityToken,
                "center_point_id": arc.centerSketchPoint.entityToken,
                "start_point_id": arc.startSketchPoint.entityToken,
                "end_point_id": arc.endSketchPoint.entityToken,
                "entity_type": "arc",
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle,
                "construction": construction
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create arc: {str(e)}")
    
    def create_polygon(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a regular polygon"""
        try:
            sketch_id = params.get('sketch_id')
            center = params.get('center')
            sides = params.get('sides')
            radius = params.get('radius')
            rotation = params.get('rotation', 0.0)
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            valid_center, msg = self.validate_point(center)
            if not valid_center:
                return self.error_response(f"Invalid center: {msg}")
            
            if not isinstance(sides, int) or sides < 3 or sides > 64:
                return self.error_response("sides must be an integer between 3 and 64")
            
            if not isinstance(radius, (int, float)) or radius <= 0:
                return self.error_response("radius must be a positive number")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Calculate polygon points
            center_pt = self.create_point_2d(center['x'], center['y'])
            points = []
            angle_step = 2 * math.pi / sides
            
            for i in range(sides):
                angle = i * angle_step + rotation
                x = center['x'] + radius * math.cos(angle)
                y = center['y'] + radius * math.sin(angle)
                points.append(self.create_point_2d(x, y))
            
            # Create polygon as connected lines
            entity_ids = []
            lines = sketch.sketchCurves.sketchLines
            
            for i in range(sides):
                start_pt = points[i]
                end_pt = points[(i + 1) % sides]  # Wrap around to close polygon
                line = lines.addByTwoPoints(start_pt, end_pt)
                
                if construction:
                    line.isConstruction = True
                
                entity_ids.append(line.entityToken)
            
            return self.success_response({
                "entity_ids": entity_ids,
                "entity_type": "polygon",
                "sides": sides,
                "radius": radius,
                "rotation": rotation,
                "construction": construction
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create polygon: {str(e)}")
    
    def create_spline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a spline curve through specified points"""
        try:
            sketch_id = params.get('sketch_id')
            points = params.get('points')
            construction = params.get('construction', False)
            
            # Validate inputs
            if not sketch_id:
                return self.error_response("sketch_id is required")
            
            if not points or len(points) < 2:
                return self.error_response("At least 2 points required for spline")
            
            # Validate all points
            for i, point in enumerate(points):
                valid, msg = self.validate_point(point)
                if not valid:
                    return self.error_response(f"Invalid point {i}: {msg}")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Ensure sketch compute is not deferred
            sketch.isComputeDeferred = False
            
            # Create spline using Point3D collection
            try:
                # Create Point3D collection
                point_collection = adsk.core.ObjectCollection.create()
                for point in points:
                    pt = adsk.core.Point3D.create(
                        float(point['x']),
                        float(point['y']),
                        0
                    )
                    point_collection.add(pt)
                
                # Create fitted spline
                spline = sketch.sketchCurves.sketchFittedSplines.add(point_collection)
                
                if not spline:
                    return self.error_response("Spline creation returned null")
                
                # Set properties
                if construction:
                    spline.isConstruction = True
                
                # Wait for operation to complete
                self.wait_for_operation_complete("spline creation")
                
                return self.success_response({
                    "entity_id": spline.entityToken,
                    "entity_type": "spline",
                    "point_count": len(points),
                    "construction": construction
                })
                
            except Exception as spline_error:
                return self.error_response(f"Spline creation failed: {str(spline_error)}")
            
        except Exception as e:
            return self.error_response(f"Failed to create spline: {str(e)}")
    
    def create_sketch_with_line(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sketch AND line in one atomic operation"""
        try:
            start_point = params.get('start_point')
            end_point = params.get('end_point')
            plane_ref = params.get('plane_reference', 'XY')
            
            # Validate inputs
            valid_start, msg1 = self.validate_point(start_point)
            if not valid_start:
                return self.error_response(f"Invalid start_point: {msg1}")
            
            valid_end, msg2 = self.validate_point(end_point)
            if not valid_end:
                return self.error_response(f"Invalid end_point: {msg2}")
            
            # MCP-safe atomic operation
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            # Ensure Design workspace
            ui.workspaces.itemById('FusionSolidEnvironment').activate()
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                return self.error_response("Active product is not a Design")
            
            rootComp = design.rootComponent
            
            # Get plane
            plane = self.get_plane_by_reference(plane_ref)
            if not plane:
                return self.error_response(f"Invalid plane reference: {plane_ref}")
            
            # Create sketch AND geometry in same context
            sketch = rootComp.sketches.add(plane)
            
            # IMMEDIATELY add geometry in same context
            start_pt = adsk.core.Point3D.create(
                float(start_point['x']), 
                float(start_point['y']), 
                0.0
            )
            end_pt = adsk.core.Point3D.create(
                float(end_point['x']), 
                float(end_point['y']), 
                0.0
            )
            
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(start_pt, end_pt)
            
            return self.success_response({
                "sketch_id": sketch.entityToken,
                "sketch_name": sketch.name,
                "line_id": line.entityToken,
                "entity_type": "line_with_sketch"
            })
            
        except Exception as e:
            return self.error_response(f"Failed to create sketch with line: {str(e)}")
