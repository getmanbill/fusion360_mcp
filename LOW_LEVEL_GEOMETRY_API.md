# Low-Level Geometry API Reference

This document describes the new low-level geometry endpoints that provide granular control over Fusion 360 sketch creation, matching the direct API patterns.

## Overview

Based on the Fusion 360 API example, we've implemented these low-level endpoints to give you fine-grained control over geometry creation:

```python
# Original Fusion 360 API example pattern:
points = adsk.core.ObjectCollection.create()
points.add(adsk.core.Point3D.create(-5, 0, 0))
points.add(adsk.core.Point3D.create(5, 1, 0))
spline = sketch1.sketchCurves.sketchFittedSplines.add(points)
print(sketch1.revisionId)  # Track changes
```

## New Endpoints

### 1. Object Collection Management

#### `fusion.create_object_collection`
Creates an ObjectCollection for managing geometry objects.

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "collection_id": "collection_140234567890",
  "collection_type": "ObjectCollection", 
  "item_count": 0
}
```

### 2. Point3D Creation

#### `fusion.create_point3d`
Creates individual Point3D objects with specified coordinates.

**Parameters:**
```json
{
  "x": 5.0,
  "y": 2.5,
  "z": 0.0
}
```

**Response:**
```json
{
  "success": true,
  "point_id": "point_140234567891",
  "coordinates": {
    "x": 5.0,
    "y": 2.5, 
    "z": 0.0
  },
  "object_type": "Point3D"
}
```

### 3. Sketch Revision Tracking

#### `fusion.get_sketch_revision_id`
Gets the current revision ID of a sketch for tracking changes.

**Parameters:**
```json
{
  "sketch_id": "sketch_token_123"
}
```

**Response:**
```json
{
  "success": true,
  "sketch_id": "sketch_token_123",
  "revision_id": "revision_456",
  "sketch_name": "Sketch1"
}
```

### 4. Fitted Spline Creation

#### `fusion.create_fitted_spline_from_points`
Creates a fitted spline using the ObjectCollection approach (like sketchFittedSplines.add()).

**Parameters:**
```json
{
  "sketch_id": "sketch_token_123",
  "points": [
    {"x": -5, "y": 0, "z": 0},
    {"x": 5, "y": 1, "z": 0},
    {"x": 6, "y": 4, "z": 3},
    {"x": 7, "y": 6, "z": 6},
    {"x": 2, "y": 3, "z": 0},
    {"x": 0, "y": 1, "z": 0}
  ],
  "construction": false
}
```

**Response:**
```json
{
  "success": true,
  "entity_id": "spline_token_789",
  "entity_type": "fitted_spline",
  "point_count": 6,
  "construction": false,
  "initial_revision_id": "revision_456",
  "final_revision_id": "revision_457",
  "collection_count": 6
}
```

## Enhanced Existing Endpoints

### Updated Rectangle Creation
The `fusion.create_rectangle` endpoint now includes revision tracking:

**Enhanced Response:**
```json
{
  "success": true,
  "entity_ids": ["line_1", "line_2", "line_3", "line_4"],
  "entity_type": "rectangle",
  "construction": false,
  "initial_revision_id": "revision_456",
  "final_revision_id": "revision_458",
  "constraints": [...]
}
```

## Complete Example Workflow

Here's how to recreate the original Fusion 360 API example using MCP endpoints:

```python
# 1. Create document and sketch
client.send_request('fusion.new_document')
sketch_result = client.send_request('fusion.create_sketch', {
    'plane_reference': 'YZ'  # rootComp.yZConstructionPlane
})
sketch_id = sketch_result['result']['sketch_id']

# 2. Get initial revision (like print(sketch1.revisionId))
revision_result = client.send_request('fusion.get_sketch_revision_id', {
    'sketch_id': sketch_id
})
print(f"Initial revision: {revision_result['result']['revision_id']}")

# 3. Create ObjectCollection (like ObjectCollection.create())
collection_result = client.send_request('fusion.create_object_collection')

# 4. Create Point3D objects (like Point3D.create())
points = [
    {'x': -5, 'y': 0, 'z': 0},
    {'x': 5, 'y': 1, 'z': 0},
    {'x': 6, 'y': 4, 'z': 3},
    {'x': 7, 'y': 6, 'z': 6},
    {'x': 2, 'y': 3, 'z': 0},
    {'x': 0, 'y': 1, 'z': 0}
]

for point in points:
    point_result = client.send_request('fusion.create_point3d', point)
    print(f"Created point: {point_result['result']['coordinates']}")

# 5. Create fitted spline (like sketchFittedSplines.add(points))
spline_result = client.send_request('fusion.create_fitted_spline_from_points', {
    'sketch_id': sketch_id,
    'points': points
})
print(f"Spline revision: {spline_result['result']['final_revision_id']}")

# 6. Create rectangle (like addTwoPointRectangle())
rect_result = client.send_request('fusion.create_rectangle', {
    'sketch_id': sketch_id,
    'corner1': {'x': 0, 'y': 0},
    'corner2': {'x': 5.0, 'y': 5.0}
})
print(f"Rectangle revision: {rect_result['result']['final_revision_id']}")

# 7. Get final revision
final_revision_result = client.send_request('fusion.get_sketch_revision_id', {
    'sketch_id': sketch_id
})
print(f"Final revision: {final_revision_result['result']['revision_id']}")
```

## Key Improvements

1. **Granular Control**: Individual Point3D and ObjectCollection creation
2. **Revision Tracking**: Track sketch changes like the native API
3. **Collection-Based Splines**: Use ObjectCollection approach for fitted splines
4. **API Consistency**: Match Fusion 360 API patterns closely
5. **Enhanced Responses**: Include revision IDs in geometry creation responses

## Testing

Use the provided `test_low_level_geometry.py` script to test all endpoints:

```bash
python test_low_level_geometry.py
```

This script demonstrates the complete workflow and validates that all low-level endpoints work correctly with revision tracking and proper geometry creation.
