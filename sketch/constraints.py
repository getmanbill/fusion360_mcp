"""
Sketch Constraints
Geometric and dimensional constraints for sketch entities
"""
import adsk.core
import adsk.fusion
from typing import Dict, Any
from .base import SketchBase

class SketchConstraints(SketchBase):
    """Handles sketch constraint operations"""
    
    def add_coincident_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make two points coincident"""
        try:
            sketch_id = params.get('sketch_id')
            point1_id = params.get('point1_id')
            point2_id = params.get('point2_id')
            
            if not all([sketch_id, point1_id, point2_id]):
                return self.error_response("sketch_id, point1_id, and point2_id are required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the points
            point1 = self._find_sketch_point(sketch, point1_id)
            point2 = self._find_sketch_point(sketch, point2_id)
            
            if not point1:
                return self.error_response(f"Point not found: {point1_id}")
            if not point2:
                return self.error_response(f"Point not found: {point2_id}")
            
            # Create coincident constraint
            constraint = sketch.geometricConstraints.addCoincident(point1, point2)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "coincident",
                "point1_id": point1_id,
                "point2_id": point2_id
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add coincident constraint: {str(e)}")
    
    def add_distance_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set distance between two entities"""
        try:
            sketch_id = params.get('sketch_id')
            entity1_id = params.get('entity1_id')
            entity2_id = params.get('entity2_id')
            distance = params.get('distance')
            parameter_name = params.get('parameter_name')
            
            if not all([sketch_id, entity1_id, entity2_id]) or distance is None:
                return self.error_response("sketch_id, entity1_id, entity2_id, and distance are required")
            
            if not isinstance(distance, (int, float)) or distance < 0:
                return self.error_response("distance must be a non-negative number")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the entities
            entity1 = self._find_sketch_entity(sketch, entity1_id)
            entity2 = self._find_sketch_entity(sketch, entity2_id)
            
            if not entity1:
                return self.error_response(f"Entity not found: {entity1_id}")
            if not entity2:
                return self.error_response(f"Entity not found: {entity2_id}")
            
            # Create distance constraint
            constraint = sketch.dimensionalConstraints.addDistanceDimension(
                entity1, entity2, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,
                adsk.core.Point2D.create(0, 0)  # Text position - will be auto-positioned
            )
            
            # Set the distance value
            if parameter_name:
                constraint.parameter.expression = parameter_name
            else:
                constraint.parameter.expression = str(distance)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "distance",
                "entity1_id": entity1_id,
                "entity2_id": entity2_id,
                "distance": distance,
                "parameter": constraint.parameter.name if constraint.parameter else None
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add distance constraint: {str(e)}")
    
    def add_parallel_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make two lines parallel"""
        try:
            sketch_id = params.get('sketch_id')
            line1_id = params.get('line1_id')
            line2_id = params.get('line2_id')
            
            if not all([sketch_id, line1_id, line2_id]):
                return self.error_response("sketch_id, line1_id, and line2_id are required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the lines
            line1 = self._find_sketch_line(sketch, line1_id)
            line2 = self._find_sketch_line(sketch, line2_id)
            
            if not line1:
                return self.error_response(f"Line not found: {line1_id}")
            if not line2:
                return self.error_response(f"Line not found: {line2_id}")
            
            # Create parallel constraint
            constraint = sketch.geometricConstraints.addParallel(line1, line2)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "parallel",
                "line1_id": line1_id,
                "line2_id": line2_id
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add parallel constraint: {str(e)}")
    
    def add_perpendicular_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make two lines perpendicular"""
        try:
            sketch_id = params.get('sketch_id')
            line1_id = params.get('line1_id')
            line2_id = params.get('line2_id')
            
            if not all([sketch_id, line1_id, line2_id]):
                return self.error_response("sketch_id, line1_id, and line2_id are required")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the lines
            line1 = self._find_sketch_line(sketch, line1_id)
            line2 = self._find_sketch_line(sketch, line2_id)
            
            if not line1:
                return self.error_response(f"Line not found: {line1_id}")
            if not line2:
                return self.error_response(f"Line not found: {line2_id}")
            
            # Create perpendicular constraint
            constraint = sketch.geometricConstraints.addPerpendicular(line1, line2)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "perpendicular",
                "line1_id": line1_id,
                "line2_id": line2_id
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add perpendicular constraint: {str(e)}")
    
    def add_radius_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set radius of circle or arc"""
        try:
            sketch_id = params.get('sketch_id')
            entity_id = params.get('entity_id')
            radius = params.get('radius')
            parameter_name = params.get('parameter_name')
            
            if not all([sketch_id, entity_id]) or radius is None:
                return self.error_response("sketch_id, entity_id, and radius are required")
            
            if not isinstance(radius, (int, float)) or radius <= 0:
                return self.error_response("radius must be a positive number")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the circular entity
            entity = self._find_circular_entity(sketch, entity_id)
            if not entity:
                return self.error_response(f"Circular entity not found: {entity_id}")
            
            # Create radius constraint
            constraint = sketch.dimensionalConstraints.addRadialDimension(
                entity, adsk.core.Point2D.create(0, 0)
            )
            
            # Set the radius value
            if parameter_name:
                constraint.parameter.expression = parameter_name
            else:
                constraint.parameter.expression = str(radius)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "radius",
                "entity_id": entity_id,
                "radius": radius,
                "parameter": constraint.parameter.name if constraint.parameter else None
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add radius constraint: {str(e)}")
    
    def add_angle_constraint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set angle between two lines"""
        try:
            sketch_id = params.get('sketch_id')
            line1_id = params.get('line1_id')
            line2_id = params.get('line2_id')
            angle = params.get('angle')
            parameter_name = params.get('parameter_name')
            
            if not all([sketch_id, line1_id, line2_id]) or angle is None:
                return self.error_response("sketch_id, line1_id, line2_id, and angle are required")
            
            if not isinstance(angle, (int, float)):
                return self.error_response("angle must be a number (radians)")
            
            sketch = self.get_sketch_by_id(sketch_id)
            if not sketch:
                return self.error_response(f"Sketch not found: {sketch_id}")
            
            # Find the lines
            line1 = self._find_sketch_line(sketch, line1_id)
            line2 = self._find_sketch_line(sketch, line2_id)
            
            if not line1:
                return self.error_response(f"Line not found: {line1_id}")
            if not line2:
                return self.error_response(f"Line not found: {line2_id}")
            
            # Create angle constraint
            constraint = sketch.dimensionalConstraints.addAngularDimension(
                line1, line2, adsk.core.Point2D.create(0, 0)
            )
            
            # Set the angle value
            if parameter_name:
                constraint.parameter.expression = parameter_name
            else:
                constraint.parameter.expression = str(angle)
            
            return self.success_response({
                "constraint_id": constraint.entityToken,
                "constraint_type": "angle",
                "line1_id": line1_id,
                "line2_id": line2_id,
                "angle": angle,
                "parameter": constraint.parameter.name if constraint.parameter else None
            })
            
        except Exception as e:
            return self.error_response(f"Failed to add angle constraint: {str(e)}")
    
    # Helper methods for finding entities
    def _find_sketch_entity(self, sketch, entity_id: str):
        """Find any sketch entity by ID"""
        # Search in all entity collections
        collections = [
            sketch.sketchCurves.sketchLines,
            sketch.sketchCurves.sketchCircles,
            sketch.sketchCurves.sketchArcs,
            sketch.sketchPoints
        ]
        
        for collection in collections:
            for entity in collection:
                if entity.entityToken == entity_id:
                    return entity
        return None
    
    def _find_sketch_point(self, sketch, point_id: str):
        """Find a sketch point by ID"""
        for point in sketch.sketchPoints:
            if point.entityToken == point_id:
                return point
        return None
    
    def _find_sketch_line(self, sketch, line_id: str):
        """Find a sketch line by ID"""
        for line in sketch.sketchCurves.sketchLines:
            if line.entityToken == line_id:
                return line
        return None
    
    def _find_circular_entity(self, sketch, entity_id: str):
        """Find a circular entity (circle or arc) by ID"""
        for circle in sketch.sketchCurves.sketchCircles:
            if circle.entityToken == entity_id:
                return circle
        for arc in sketch.sketchCurves.sketchArcs:
            if arc.entityToken == entity_id:
                return arc
        return None
