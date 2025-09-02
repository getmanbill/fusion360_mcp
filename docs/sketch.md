# Fusion 360 Sketch MCP Specification

## Overview

This specification defines MCP tools for automating Fusion 360 sketch operations, enabling programmatic creation and manipulation of 2D sketches for parametric design workflows.

## Core Capabilities

### Sketch Management
- Create, activate, and manage sketches
- Associate sketches with planes and faces
- Query sketch properties and contents
- Sketch lifecycle management

### Geometry Creation
- Basic shapes (rectangles, circles, lines, arcs)
- Advanced curves (splines, polygons, ellipses)
- Construction geometry and reference elements
- Point and coordinate management

### Constraints & Relationships
- Geometric constraints (parallel, perpendicular, tangent, etc.)
- Dimensional constraints (distance, angle, radius)
- Parametric relationships with user parameters
- Constraint validation and conflict resolution

### Pattern & Transform Operations
- Rectangular and circular patterns
- Mirror operations
- Offset and scaling transformations
- Sketch entity modification tools

## Tool Categories

## 1. Sketch Management

### `fusion.create_sketch`
Creates a new sketch on the specified plane or face.

**Parameters:**
- `plane_reference` (string) - Plane name ("XY", "XZ", "YZ") or face ID
- `name` (string, optional) - Custom sketch name

**Returns:**
- `sketch_id` (string) - Unique identifier for the created sketch
- `plane_info` (object) - Information about the sketch plane
- `status` (string) - Creation status

### `fusion.list_sketches`
Lists all sketches in the active design.

**Returns:**
- `sketches` (array) - Array of sketch objects with:
  - `id` (string) - Sketch identifier
  - `name` (string) - Sketch name
  - `plane` (string) - Associated plane/face
  - `entity_count` (number) - Number of sketch entities
  - `is_active` (boolean) - Whether sketch is currently active
  - `is_fully_constrained` (boolean) - Constraint status

### `fusion.activate_sketch`
Activates a sketch for editing.

**Parameters:**
- `sketch_id` (string) - Target sketch identifier

### `fusion.finish_sketch`
Exits sketch editing mode.

**Parameters:**
- `sketch_id` (string) - Target sketch identifier

### `fusion.get_sketch_info`
Retrieves detailed information about a sketch.

**Parameters:**
- `sketch_id` (string) - Target sketch identifier

**Returns:**
- `entities` (array) - All sketch entities
- `constraints` (array) - Applied constraints
- `parameters` (array) - Associated parameters
- `bounding_box` (object) - Sketch extents

## 2. Basic Geometry Creation

### `fusion.create_rectangle`
Creates a rectangle in the active sketch.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `corner1` (object) - First corner coordinates `{x, y}`
- `corner2` (object) - Opposite corner coordinates `{x, y}`
- `construction` (boolean, optional) - Create as construction geometry

**Returns:**
- `entity_ids` (array) - IDs of created lines
- `constraints` (array) - Auto-applied constraints

### `fusion.create_circle`
Creates a circle in the active sketch.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `center` (object) - Center point coordinates `{x, y}`
- `radius` (number) - Circle radius
- `construction` (boolean, optional) - Create as construction geometry

**Returns:**
- `entity_id` (string) - Created circle ID
- `center_point_id` (string) - Center point ID

### `fusion.create_line`
Creates a line between two points.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `start_point` (object) - Start coordinates `{x, y}`
- `end_point` (object) - End coordinates `{x, y}`
- `construction` (boolean, optional) - Create as construction geometry

**Returns:**
- `entity_id` (string) - Created line ID
- `start_point_id` (string) - Start point ID
- `end_point_id` (string) - End point ID

### `fusion.create_arc`
Creates an arc by center, start angle, and end angle.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `center` (object) - Center point coordinates `{x, y}`
- `radius` (number) - Arc radius
- `start_angle` (number) - Start angle in radians
- `end_angle` (number) - End angle in radians
- `construction` (boolean, optional) - Create as construction geometry

## 3. Advanced Geometry

### `fusion.create_polygon`
Creates a regular polygon.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `center` (object) - Center coordinates `{x, y}`
- `sides` (number) - Number of sides (3-64)
- `radius` (number) - Circumscribed radius
- `rotation` (number, optional) - Rotation angle in radians

### `fusion.create_spline`
Creates a spline curve through specified points.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `points` (array) - Array of point coordinates `[{x, y}, ...]`
- `tangents` (array, optional) - Tangent vectors at points
- `closed` (boolean, optional) - Create closed spline

### `fusion.create_ellipse`
Creates an ellipse.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `center` (object) - Center coordinates `{x, y}`
- `major_axis` (number) - Major axis length
- `minor_axis` (number) - Minor axis length
- `rotation` (number, optional) - Rotation angle in radians

## 4. Constraints

### `fusion.add_coincident_constraint`
Makes two points coincident.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `point1_id` (string) - First point entity ID
- `point2_id` (string) - Second point entity ID

### `fusion.add_distance_constraint`
Sets distance between two entities.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity1_id` (string) - First entity ID
- `entity2_id` (string) - Second entity ID
- `distance` (number) - Target distance
- `parameter_name` (string, optional) - Link to user parameter

### `fusion.add_parallel_constraint`
Makes two lines parallel.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `line1_id` (string) - First line entity ID
- `line2_id` (string) - Second line entity ID

### `fusion.add_perpendicular_constraint`
Makes two lines perpendicular.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `line1_id` (string) - First line entity ID
- `line2_id` (string) - Second line entity ID

### `fusion.add_radius_constraint`
Sets radius of circle or arc.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity_id` (string) - Circle or arc entity ID
- `radius` (number) - Target radius
- `parameter_name` (string, optional) - Link to user parameter

### `fusion.add_angle_constraint`
Sets angle between two lines.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `line1_id` (string) - First line entity ID
- `line2_id` (string) - Second line entity ID
- `angle` (number) - Target angle in radians
- `parameter_name` (string, optional) - Link to user parameter

## 5. Pattern Operations

### `fusion.create_rectangular_pattern`
Creates a rectangular pattern of sketch entities.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity_ids` (array) - Entities to pattern
- `x_direction` (object) - X direction vector `{x, y}`
- `y_direction` (object) - Y direction vector `{x, y}`
- `x_count` (number) - Number of instances in X
- `y_count` (number) - Number of instances in Y
- `x_spacing` (number) - Spacing in X direction
- `y_spacing` (number) - Spacing in Y direction

### `fusion.create_circular_pattern`
Creates a circular pattern of sketch entities.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity_ids` (array) - Entities to pattern
- `center_point` (object) - Center of rotation `{x, y}`
- `total_angle` (number) - Total angle in radians
- `count` (number) - Number of instances

### `fusion.mirror_entities`
Mirrors sketch entities across a line.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity_ids` (array) - Entities to mirror
- `mirror_line_id` (string) - Mirror line entity ID

## 6. Transform Operations

### `fusion.offset_entities`
Creates offset copies of sketch entities.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entity_ids` (array) - Entities to offset
- `offset_distance` (number) - Offset distance (positive = outward)
- `chain_selection` (boolean, optional) - Automatically chain connected entities

### `fusion.trim_entities`
Trims sketch entities to boundaries.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entities_to_trim` (array) - Entity IDs to trim
- `trim_tool_id` (string) - Boundary entity ID

### `fusion.extend_entities`
Extends sketch entities to boundaries.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `entities_to_extend` (array) - Entity IDs to extend
- `boundary_id` (string) - Boundary entity ID

## 7. Import/Export

### `fusion.import_dxf_to_sketch`
Imports DXF file contents into a sketch.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `dxf_path` (string) - Path to DXF file
- `scale` (number, optional) - Import scale factor
- `merge_curves` (boolean, optional) - Merge connected curves

**Returns:**
- `imported_entities` (array) - IDs of imported entities
- `import_summary` (object) - Import statistics

### `fusion.export_sketch_to_dxf`
Exports sketch to DXF format.

**Parameters:**
- `sketch_id` (string) - Source sketch
- `output_path` (string) - Output file path
- `version` (string, optional) - DXF version ("R14", "2000", "2004", etc.)

### `fusion.create_sketch_from_json`
Creates sketch from JSON definition.

**Parameters:**
- `sketch_data` (object) - Complete sketch definition including:
  - `plane` (string) - Target plane
  - `entities` (array) - Entity definitions
  - `constraints` (array) - Constraint definitions
  - `parameters` (object) - Parameter mappings

### `fusion.export_sketch_to_json`
Exports sketch to JSON format.

**Parameters:**
- `sketch_id` (string) - Source sketch
- `include_constraints` (boolean, optional) - Include constraint data
- `include_parameters` (boolean, optional) - Include parameter links

## Use Case Examples

### Parametric Bracket Generation
```json
{
  "method": "fusion.create_sketch",
  "params": {"plane_reference": "XY", "name": "bracket_profile"}
}
```

### Automated Pattern Creation
```json
{
  "method": "fusion.create_rectangular_pattern",
  "params": {
    "sketch_id": "sketch_001",
    "entity_ids": ["circle_001"],
    "x_count": 5,
    "y_count": 3,
    "x_spacing": 10,
    "y_spacing": 8
  }
}
```

### DXF Import Workflow
```json
{
  "method": "fusion.import_dxf_to_sketch",
  "params": {
    "sketch_id": "sketch_002", 
    "dxf_path": "/path/to/drawing.dxf",
    "scale": 1.0
  }
}
```

## Implementation Notes

### Coordinate System
- All coordinates are in sketch space (2D)
- Units follow the design's default units
- Origin (0,0) is at sketch origin

### Entity References
- All entities have unique string IDs within their sketch
- IDs persist for the sketch lifetime
- Cross-sketch references not supported

### Constraint Behavior
- Auto-constraints may be applied during creation
- Constraint conflicts return descriptive errors
- Over-constrained sketches are flagged but allowed

### Performance Considerations
- Batch operations when possible for large patterns
- Sketch updates are deferred until finish_sketch()
- Complex splines and patterns may have creation limits

## Error Handling

### Common Error Codes
- `SKETCH_NOT_FOUND` - Invalid sketch ID
- `CONSTRAINT_CONFLICT` - Constraint cannot be applied
- `INVALID_GEOMETRY` - Geometry parameters invalid
- `SKETCH_NOT_ACTIVE` - Operation requires active sketch
- `ENTITY_NOT_FOUND` - Referenced entity doesn't exist

### Validation
- Geometry parameters validated before creation
- Constraint compatibility checked
- Parameter references verified

## Future Enhancements

- 3D sketch support
- Advanced spline controls (NURBS parameters)
- Sketch analysis tools (area, perimeter calculations)
- Automated constraint inference
- Sketch comparison and diff tools
- Integration with simulation for sketch optimization
