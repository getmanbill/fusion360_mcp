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

## 0. Document Management

### `fusion.new_document`
Creates a new Fusion 360 document.

**Parameters:**
- `document_type` (string, optional) - Document type ("FusionDesignDocumentType")

**Returns:**
- `document_name` (string) - Name of created document
- `document_id` (string) - Document identifier
- `product_type` (string) - Product object type
- `design_id` (string) - Design object type
- `root_component_id` (string) - Root component identifier

### `fusion.get_root_component`
Gets the root component of the active design.

**Returns:**
- `root_component_id` (string) - Component identifier
- `root_component_token` (string) - Entity token
- `design_type` (string) - Design type
- `sketches_count` (number) - Number of sketches
- `features_count` (number) - Number of features

### `fusion.get_document_info`
Gets information about the active document.

**Returns:**
- `document_name` (string) - Document name
- `document_path` (string) - Document path or "Unsaved"
- `design_type` (string) - Design type
- `units` (string) - Default length units

### `fusion.save_document`
Saves the active document if modified.

**Returns:**
- `document_name` (string) - Document name
- `saved` (boolean) - Whether save occurred
- `message` (string, optional) - Status message

## 0.1. Parameter Management

### `fusion.list_parameters`
Lists all user parameters in the active document.

**Returns:**
- `parameters` (array) - Array of parameter objects with:
  - `name` (string) - Parameter name
  - `expression` (string) - Parameter expression
  - `value` (number) - Evaluated value
  - `units` (string) - Parameter units
  - `comment` (string) - Parameter comment
- `count` (number) - Total parameter count

### `fusion.set_parameter`
Sets or creates a user parameter.

**Parameters:**
- `name` (string) - Parameter name
- `value` (number) - Parameter value
- `units` (string, optional) - Parameter units

**Returns:**
- `parameter` (object) - Parameter information
- `created` (boolean, optional) - Whether parameter was created

### `fusion.get_parameter`
Gets information about a specific parameter.

**Parameters:**
- `name` (string) - Parameter name

**Returns:**
- `parameter` (object) - Parameter information

### `fusion.delete_parameter`
Deletes a user parameter.

**Parameters:**
- `name` (string) - Parameter name

**Returns:**
- `deleted_parameter` (string) - Name of deleted parameter

## 0.2. Atomic Operations

### `fusion.create_sketch_with_line_atomic`
Atomically creates a sketch and adds a line in a single transaction.

**Parameters:**
- `start_point` (object) - Start coordinates `{x, y, z}`
- `end_point` (object) - End coordinates `{x, y, z}`
- `plane_reference` (string, optional) - Plane ("XY", "XZ", "YZ")

**Returns:**
- `sketch_id` (string) - Created sketch identifier
- `line_id` (string) - Created line identifier
- `success` (boolean) - Operation success status

### `fusion.create_sketch_with_rectangle_atomic`
Atomically creates a sketch and adds a rectangle in a single transaction.

**Parameters:**
- `corner1` (object) - First corner coordinates `{x, y, z}`
- `corner2` (object) - Opposite corner coordinates `{x, y, z}`
- `plane_reference` (string, optional) - Plane ("XY", "XZ", "YZ")

**Returns:**
- `sketch_id` (string) - Created sketch identifier
- `entity_ids` (array) - Array of created line IDs
- `success` (boolean) - Operation success status

### `fusion.create_sketch_with_circle_atomic`
Atomically creates a sketch and adds a circle in a single transaction.

**Parameters:**
- `center` (object) - Center coordinates `{x, y, z}`
- `radius` (number) - Circle radius
- `plane_reference` (string, optional) - Plane ("XY", "XZ", "YZ")

**Returns:**
- `sketch_id` (string) - Created sketch identifier
- `circle_id` (string) - Created circle identifier
- `success` (boolean) - Operation success status

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

### `fusion.delete_sketch`
Deletes a sketch from the design.

**Parameters:**
- `sketch_id` (string) - Target sketch identifier

**Returns:**
- `success` (boolean) - Deletion success status
- `deleted_sketch_id` (string) - ID of deleted sketch

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

### `fusion.create_fitted_spline_from_points`
Creates a fitted spline from Point3D objects (like sketchFittedSplines.add()).

**Parameters:**
- `sketch_id` (string) - Target sketch
- `points` (array) - Array of 3D point coordinates `[{x, y, z}, ...]`

**Returns:**
- `entity_id` (string) - Created spline ID
- `point_count` (number) - Number of points used
- `initial_revision_id` (string) - Sketch revision before operation
- `final_revision_id` (string) - Sketch revision after operation

### `fusion.add_two_point_rectangle`
Creates a rectangle using two corner points (like addTwoPointRectangle()).

**Parameters:**
- `sketch_id` (string) - Target sketch
- `start_point` (object) - First corner coordinates `{x, y, z}`
- `end_point` (object) - Opposite corner coordinates `{x, y, z}`

**Returns:**
- `entity_ids` (array) - Array of created line IDs
- `line_count` (number) - Number of lines created
- `method` (string) - Creation method used
- `initial_revision_id` (string) - Sketch revision before operation
- `final_revision_id` (string) - Sketch revision after operation

### `fusion.create_ellipse`
Creates an ellipse.

**Parameters:**
- `sketch_id` (string) - Target sketch
- `center` (object) - Center coordinates `{x, y}`
- `major_axis` (number) - Major axis length
- `minor_axis` (number) - Minor axis length
- `rotation` (number, optional) - Rotation angle in radians

## 3.1. Point and Collection Utilities

### `fusion.create_point3d`
Creates a Point3D object (like Point3D.create()).

**Parameters:**
- `x` (number) - X coordinate
- `y` (number) - Y coordinate
- `z` (number) - Z coordinate

**Returns:**
- `coordinates` (object) - Point coordinates `{x, y, z}`
- `success` (boolean) - Creation success status

### `fusion.create_object_collection`
Creates an ObjectCollection (like ObjectCollection.create()).

**Returns:**
- `collection_id` (string) - Collection identifier
- `collection_type` (string) - Collection type
- `item_count` (number) - Number of items in collection

### `fusion.get_sketch_revision_id`
Gets the current revision ID of a sketch.

**Parameters:**
- `sketch_id` (string) - Target sketch identifier

**Returns:**
- `revision_id` (string) - Current sketch revision ID

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

## 8. Testing and Debugging

### `fusion.test_direct_sketch`
Direct test method for sketch creation and geometry addition.

**Returns:**
- `success` (boolean) - Test execution success
- `sketch_created` (boolean) - Whether sketch was created
- `line_created` (boolean) - Whether line was added
- `test_results` (object) - Detailed test results

### `fusion.create_sketch_with_line`
Combined sketch creation and line addition for testing.

**Parameters:**
- `start_point` (object) - Start coordinates `{x, y}`
- `end_point` (object) - End coordinates `{x, y}`
- `plane_reference` (string, optional) - Plane reference

**Returns:**
- `sketch_id` (string) - Created sketch ID
- `line_id` (string) - Created line ID
- `success` (boolean) - Operation success

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

## Key Lessons from test_exact_example_script.py

### Exact API Replication Pattern
The test script demonstrates a **precise step-by-step replication** of the original Fusion 360 API workflow:
- Document creation → Root component access → Sketch creation → Geometry addition
- Each step mirrors the exact sequence: `app.documents.add()` → `design.rootComponent` → `sketches.add()` → geometry operations
- This pattern ensures compatibility and predictable behavior with existing Fusion 360 workflows

### Robust Error Handling and Debugging
The script shows **extensive defensive programming practices**:
- Multiple field name attempts (`sketch_id`, `id`, `entity_id`) for safe data extraction
- Comprehensive debugging with type checking and attribute inspection
- Pause points for manual verification during testing
- Graceful fallbacks when operations fail
- Never assume field names - always use `.get()` with safe defaults

### Revision ID Tracking
**Critical insight**: The script tracks `revisionId` at key points:
- Initial sketch creation
- After spline addition  
- After rectangle addition

This suggests **revision tracking is essential** for understanding when geometry changes are committed and for debugging geometry operations.

### Two-Phase Geometry Creation
The workflow demonstrates **two distinct geometry creation patterns**:

**Phase 1: Complex Curves (Splines)**
- Create Point3D collection first
- Add multiple points with coordinates
- Create fitted spline from point collection
- Requires ObjectCollection management

**Phase 2: Simple Shapes (Rectangle)**  
- Create start/end Point3D objects
- Use dedicated shape methods (`addTwoPointRectangle`)
- Direct coordinate-based approach

### Sketch State Management
**Critical requirement**: Sketches must be properly activated before adding geometry:
```python
# Must ensure sketch is properly in edit mode
if app.activeEditObject != sketch:
    sketch.edit()  # Put sketch in edit mode
```

This shows **sketch activation is mandatory** before adding geometry operations.

### MCP Communication Best Practices
The script uses a **consistent request/response pattern**:
- Socket-based JSON communication with proper encoding
- Standardized method naming (`fusion.create_sketch`, `fusion.add_two_point_rectangle`)
- Parameter validation and safe field extraction
- Always handle both success and error response structures

### 3D Coordinate System Understanding
The geometry uses **3D coordinates consistently**:
- All points have x, y, z values (even for 2D sketches, z=0)
- YZ plane is used as the sketch plane reference
- Rectangle corners and spline points are defined in 3D space
- Coordinate validation must handle all three dimensions

### Progressive Complexity Workflow
The workflow shows **increasing operational complexity**:
1. Simple document/sketch setup (foundational operations)
2. Point creation (basic object instantiation)
3. Complex spline (multiple points, fitted curve algorithms)
4. Geometric shapes (specialized methods with auto-constraints)

### Validation and Safety Patterns
**Extensive validation is required at every step**:
- Point coordinate validation before creation
- Sketch existence checking before operations
- Active design verification before document operations
- Parameter type checking with meaningful error messages
- Always validate response structure before field access

### Timing and Synchronization
The code includes **wait mechanisms for asynchronous operations**:
- `wait_for_operation_complete()` after major operations
- `wait_for_fusion_ready()` before state-dependent operations
- Manual pause points for verification in testing
- This suggests **Fusion 360 operations are asynchronous** and require careful timing

### Additional Method Patterns Discovered

**Atomic Operations Pattern**: The codebase includes atomic operations that create sketch + geometry in single transactions:
- `fusion.create_sketch_with_line_atomic` - Creates sketch and line atomically
- `fusion.create_sketch_with_rectangle_atomic` - Creates sketch and rectangle atomically  
- `fusion.create_sketch_with_circle_atomic` - Creates sketch and circle atomically

These follow a **transaction-based approach**:
```python
# 1. Validate all inputs BEFORE creating sketch
# 2. Create sketch
# 3. Add geometry in same operation
# 4. Rollback entire operation if any step fails
```

**Thread Safety Patterns**: All methods follow strict thread safety requirements:
- **Main thread execution**: All Fusion API calls use custom events to execute on main UI thread
- **Operation marshaling**: Socket handlers never call Fusion API directly
- **Progress monitoring**: Long operations include progress logging at 5-second intervals
- **Request cleanup**: Automatic cleanup of failed/timed-out requests

**Point3D Creation Standardization**: All geometry methods use unified Point3D creation:
- **Safe creation**: `create_safe_point3d()` prevents lifecycle errors
- **Input validation**: Comprehensive coordinate validation and type checking
- **Range validation**: Prevents extreme coordinates that could cause crashes
- **Coordinate space consistency**: Model-to-sketch space conversion

**Document Operation Patterns**: Document handlers follow specific patterns:
- `fusion.new_document` - Creates new document like `app.documents.add(DocumentTypes.FusionDesignDocumentType)`
- `fusion.get_root_component` - Gets root component like `design.rootComponent`
- `fusion.get_document_info` - Retrieves active document information
- `fusion.save_document` - Safe document saving with modification checks

**Parameter Management Patterns**: Parameter handlers demonstrate:
- **Safe iteration**: Error handling for each parameter during listing
- **Expression handling**: Proper Fusion expression format for values with units
- **Creation vs Update**: Different logic for new vs existing parameters
- **Value input handling**: Using `ValueInput.createByString()` for parameter creation

**Constraint Application Patterns**: Constraint handlers show:
- **Entity lookup**: Systematic search across all entity collections
- **Type-specific methods**: Different finder methods for points, lines, circular entities
- **Parameter linking**: Optional parameter name linking for constraints
- **Auto-positioning**: Automatic positioning for dimension text

**Crash-Safe Testing Patterns**: The testing system demonstrates:
- **Comprehensive logging**: Every API call logged with timestamps and context
- **State snapshots**: Thread info, Fusion state, operation stack tracking  
- **Recovery mechanisms**: Automatic state restoration on failures
- **Detailed reporting**: JSON reports for debugging and analysis

### Key Takeaway
**Successful geometry addition requires meticulous attention to API state, error handling, and the exact sequence of operations** that Fusion 360 expects. The MCP layer abstracts this complexity but must maintain the same fundamental patterns for reliability and predictability. The atomic operations, thread safety measures, and crash-safe testing patterns are essential for production-ready implementations.

## Implementation Notes

### Coordinate System
- All coordinates are in sketch space (2D) but specified as 3D points
- Units follow the design's default units
- Origin (0,0,0) is at sketch origin
- Z-coordinate typically 0 for 2D sketches

### Entity References
- All entities have unique string IDs within their sketch
- IDs persist for the sketch lifetime
- Cross-sketch references not supported
- Always validate entity existence before operations

### Constraint Behavior
- Auto-constraints may be applied during creation
- Constraint conflicts return descriptive errors
- Over-constrained sketches are flagged but allowed
- Revision IDs change when constraints are applied

### Performance Considerations
- Batch operations when possible for large patterns
- Sketch updates are deferred until finish_sketch()
- Complex splines and patterns may have creation limits
- Always wait for operations to complete before next step

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
