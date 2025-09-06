"""
External Real Test for Arc Operations
Tests the actual deployed arc_operations.py methods directly with realistic mocks
"""
import sys
import os
import logging
from datetime import datetime

# Add the fusion_addon directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fusion_addon'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'arc_operations_external_real_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Create mock Fusion 360 modules before importing arc operations
class MockPoint2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    @staticmethod
    def create(x, y):
        return MockPoint2D(x, y)

class MockPoint3D:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

class MockSketchPoint:
    def __init__(self, x, y):
        self.entityToken = f"mock_point_{id(self)}"
        self.geometry = MockPoint3D(x, y)

class MockArc3D:
    def __init__(self):
        self.center = MockPoint3D(0, 0, 0)
        self.startAngle = 0
        self.endAngle = 1.57
        self.sweepAngle = 1.57

class MockBoundingBox3D:
    def __init__(self):
        self.minPoint = MockPoint3D(-5, -5, 0)
        self.maxPoint = MockPoint3D(5, 5, 0)

class MockSketchArc:
    def __init__(self):
        self.entityToken = f"mock_arc_{id(self)}"
        self.radius = 5.0
        self.length = 15.7
        self.isConstruction = False
        self.is2D = True
        self.isDeletable = True
        self.isFixed = False
        self.isFullyConstrained = False
        self.isLinked = False
        self.isReference = False
        self.isVisible = True
        self.objectType = "adsk::fusion::SketchArc"
        
        # Create mock points
        self.centerSketchPoint = MockSketchPoint(0, 0)
        self.startSketchPoint = MockSketchPoint(5, 0)
        self.endSketchPoint = MockSketchPoint(0, 5)
        
        # Create mock geometry and bounding box
        self.geometry = MockArc3D()
        self.boundingBox = MockBoundingBox3D()
        
        # Mock constraints and dimensions
        self.geometricConstraints = []
        self.sketchDimensions = []
        self.intersections = []
    
    def breakCurve(self, point):
        return [MockSketchArc(), MockSketchArc()]
    
    def extend(self, point):
        pass
    
    def split(self, point):
        return [MockSketchArc(), MockSketchArc()]
    
    def trim(self, point):
        pass

class MockSketchArcs:
    def __init__(self):
        self.arcs = []
    
    def addByThreePoints(self, p1, p2, p3):
        arc = MockSketchArc()
        self.arcs.append(arc)
        return arc
    
    def addByCenterStartSweep(self, center, start, sweep):
        arc = MockSketchArc()
        self.arcs.append(arc)
        return arc
    
    def addFillet(self, curve1, curve2, radius):
        arc = MockSketchArc()
        self.arcs.append(arc)
        return arc
    
    def __iter__(self):
        return iter(self.arcs)

class MockSketchCurves:
    def __init__(self):
        self.sketchArcs = MockSketchArcs()
        self.sketchLines = MockSketchArcs()  # Simplified
        self.sketchCircles = MockSketchArcs()  # Simplified
        self.sketchEllipses = MockSketchArcs()  # Simplified
        self.sketchSplines = MockSketchArcs()  # Simplified

class MockSketch:
    def __init__(self):
        self.entityToken = f"mock_sketch_{id(self)}"
        self.sketchCurves = MockSketchCurves()
        self.name = "TestSketch"

# Mock the adsk modules
class MockCore:
    Point2D = MockPoint2D

class MockFusion:
    class Design:
        pass
    
    class Sketch:
        pass
    
    class Component:
        pass

class MockAdsk:
    def __init__(self):
        self.core = MockCore()
        self.fusion = MockFusion()

# Install mocks
mock_adsk = MockAdsk()
sys.modules['adsk'] = mock_adsk
sys.modules['adsk.core'] = mock_adsk.core
sys.modules['adsk.fusion'] = mock_adsk.fusion

# Now import the real arc operations
from sketch.geometry.arc_operations import ArcOperations

class MockArcOperationsBase:
    """Enhanced mock base class that simulates real Fusion API behavior"""
    
    def __init__(self):
        self.sketches = {}
        
    def get_sketch_by_id(self, sketch_id):
        return self.sketches.get(sketch_id)
    
    def validate_point(self, point):
        if not isinstance(point, dict):
            return False, "Point must be a dictionary"
        if 'x' not in point or 'y' not in point:
            return False, "Point must have x and y coordinates"
        if not isinstance(point['x'], (int, float)) or not isinstance(point['y'], (int, float)):
            return False, "Point coordinates must be numbers"
        return True, "Valid point"
    
    def create_point_2d(self, x, y):
        return MockPoint2D.create(x, y)
    
    def success_response(self, data):
        return {"success": True, "data": data}
    
    def error_response(self, message):
        return {"success": False, "error": message}

def test_arc_creation_methods_real():
    """Test arc creation methods with real ArcOperations class"""
    logging.info("Testing real arc creation methods with actual ArcOperations class...")
    
    # Create real ArcOperations instance
    arc_ops = ArcOperations()
    
    # Create a mock sketch and register it
    sketch = MockSketch()
    sketch_id = sketch.entityToken
    arc_ops.sketches = {sketch_id: sketch}  # Add sketches dict to arc_ops for testing
    
    logging.info(f"Created test sketch: {sketch_id}")
    
    # Test 1: Create arc by three points
    logging.info("Testing create_arc_by_three_points...")
    params = {
        'sketch_id': sketch_id,
        'point1': {'x': 0, 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5},
        'construction': False
    }
    
    result = arc_ops.create_arc_by_three_points(params)
    if result.get('success'):
        arc1_id = result['data']['arc_id']
        logging.info(f"[PASS] create_arc_by_three_points: Created arc {arc1_id}")
        logging.info(f"  Radius: {result['data']['radius']}")
    else:
        logging.error(f"[FAIL] create_arc_by_three_points: {result.get('error')}")
        return False
    
    # Test 2: Create arc by center, start point, and sweep angle
    logging.info("Testing create_arc_by_center_start_sweep...")
    params = {
        'sketch_id': sketch_id,
        'center': {'x': 10, 'y': 0},
        'start_point': {'x': 15, 'y': 0},
        'sweep_angle': 1.57,  # 90 degrees in radians
        'construction': False
    }
    
    result = arc_ops.create_arc_by_center_start_sweep(params)
    if result.get('success'):
        arc2_id = result['data']['arc_id']
        logging.info(f"[PASS] create_arc_by_center_start_sweep: Created arc {arc2_id}")
        logging.info(f"  Radius: {result['data']['radius']}")
        logging.info(f"  Sweep angle: {result['data']['sweep_angle']}")
    else:
        logging.error(f"[FAIL] create_arc_by_center_start_sweep: {result.get('error')}")
        return False
    
    # Test 3: Create mock curves for fillet testing
    logging.info("Creating mock curves for fillet test...")
    curve1 = MockSketchArc()  # Using MockSketchArc as a general curve
    curve2 = MockSketchArc()
    curve1_id = curve1.entityToken
    curve2_id = curve2.entityToken
    
    # Add curves to sketch for _find_sketch_curve to find
    sketch.sketchCurves.sketchLines.arcs.extend([curve1, curve2])
    logging.info(f"Created mock curves: {curve1_id}, {curve2_id}")
    
    # Test 4: Create fillet arc
    logging.info("Testing create_arc_fillet...")
    params = {
        'sketch_id': sketch_id,
        'curve1_id': curve1_id,
        'curve2_id': curve2_id,
        'radius': 1.0,
        'construction': False
    }
    
    result = arc_ops.create_arc_fillet(params)
    if result.get('success'):
        arc3_id = result['data']['arc_id']
        logging.info(f"[PASS] create_arc_fillet: Created fillet arc {arc3_id}")
        logging.info(f"  Radius: {result['data']['radius']}")
    else:
        logging.error(f"[FAIL] create_arc_fillet: {result.get('error')}")
        return False
    
    return True, sketch_id, arc1_id, arc2_id, arc3_id

def test_arc_query_methods_real(sketch_id, arc_id):
    """Test arc query methods with real ArcOperations class"""
    logging.info("Testing real arc query methods with actual ArcOperations class...")
    
    # Create real ArcOperations instance
    arc_ops = ArcOperations()
    
    # Set up the sketch with a mock arc
    sketch = MockSketch()
    test_arc = MockSketchArc()
    test_arc.entityToken = arc_id  # Use the passed arc_id
    sketch.sketchCurves.sketchArcs.arcs.append(test_arc)
    arc_ops.sketches = {sketch_id: sketch}
    
    # Test get_arc_properties
    logging.info("Testing get_arc_properties...")
    params = {
        'sketch_id': sketch_id,
        'arc_id': arc_id
    }
    
    result = arc_ops.get_arc_properties(params)
    if result.get('success'):
        logging.info(f"[PASS] get_arc_properties: Arc {arc_id}")
        logging.info(f"  Radius: {result['data']['radius']}")
        logging.info(f"  Length: {result['data']['length']}")
        logging.info(f"  Start angle: {result['data']['start_angle']}")
        logging.info(f"  End angle: {result['data']['end_angle']}")
        logging.info(f"  Sweep angle: {result['data']['sweep_angle']}")
    else:
        logging.error(f"[FAIL] get_arc_properties: {result.get('error')}")
        return False
    
    # Test get_arc_state
    logging.info("Testing get_arc_state...")
    result = arc_ops.get_arc_state(params)
    if result.get('success'):
        logging.info(f"[PASS] get_arc_state: Arc {arc_id}")
        logging.info(f"  Is construction: {result['data']['is_construction']}")
        logging.info(f"  Is deletable: {result['data']['is_deletable']}")
        logging.info(f"  Is fixed: {result['data']['is_fixed']}")
        logging.info(f"  Is visible: {result['data']['is_visible']}")
    else:
        logging.error(f"[FAIL] get_arc_state: {result.get('error')}")
        return False
    
    # Test get_arc_constraints
    logging.info("Testing get_arc_constraints...")
    result = arc_ops.get_arc_constraints(params)
    if result.get('success'):
        logging.info(f"[PASS] get_arc_constraints: Arc {arc_id}")
        logging.info(f"  Constraint count: {result['data']['constraint_count']}")
        logging.info(f"  Dimension count: {result['data']['dimension_count']}")
    else:
        logging.error(f"[FAIL] get_arc_constraints: {result.get('error')}")
        return False
    
    # Test get_arc_intersections
    logging.info("Testing get_arc_intersections...")
    result = arc_ops.get_arc_intersections(params)
    if result.get('success'):
        logging.info(f"[PASS] get_arc_intersections: Arc {arc_id}")
        logging.info(f"  Intersection count: {result['data']['intersection_count']}")
    else:
        logging.error(f"[FAIL] get_arc_intersections: {result.get('error')}")
        return False
    
    return True

def test_arc_manipulation_methods_real(sketch_id, arc_id):
    """Test arc manipulation methods with real ArcOperations class"""
    logging.info("Testing real arc manipulation methods with actual ArcOperations class...")
    
    # Create real ArcOperations instance
    arc_ops = ArcOperations()
    
    # Set up the sketch with a mock arc
    sketch = MockSketch()
    test_arc = MockSketchArc()
    test_arc.entityToken = arc_id  # Use the passed arc_id
    sketch.sketchCurves.sketchArcs.arcs.append(test_arc)
    arc_ops.sketches = {sketch_id: sketch}
    
    # Test split_arc
    logging.info("Testing split_arc...")
    params = {
        'sketch_id': sketch_id,
        'arc_id': arc_id,
        'split_point': {'x': 2.5, 'y': 2.5}  # Point on the arc
    }
    
    result = arc_ops.split_arc(params)
    if result.get('success'):
        logging.info(f"[PASS] split_arc: Split arc {arc_id}")
        logging.info(f"  Created {len(result['data']['split_curves'])} curves")
        # Note: arc_id is no longer valid after splitting
    else:
        logging.error(f"[FAIL] split_arc: {result.get('error')}")
        return False
    
    # Test break_arc_curve
    logging.info("Testing break_arc_curve...")
    params = {
        'sketch_id': sketch_id,
        'arc_id': arc_id,
        'break_point': {'x': 3.5, 'y': 3.5}  # Point on the arc
    }
    
    result = arc_ops.break_arc_curve(params)
    if result.get('success'):
        logging.info(f"[PASS] break_arc_curve: Broke arc {arc_id}")
        logging.info(f"  Created {len(result['data']['broken_curves'])} curves")
    else:
        logging.error(f"[FAIL] break_arc_curve: {result.get('error')}")
        return False
    
    return True

def test_error_handling_real():
    """Test error handling with real ArcOperations class"""
    logging.info("Testing real error handling with actual ArcOperations class...")
    
    # Create real ArcOperations instance
    arc_ops = ArcOperations()
    
    # Test with invalid sketch ID
    params = {
        'sketch_id': 'invalid_sketch_id',
        'point1': {'x': 0, 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5}
    }
    
    result = arc_ops.create_arc_by_three_points(params)
    if not result.get('success'):
        logging.info("[PASS] Error handling: Invalid sketch ID correctly rejected")
    else:
        logging.error("[FAIL] Error handling: Should have failed with invalid sketch ID")
        return False
    
    # Test with invalid point coordinates
    params = {
        'sketch_id': 'any_sketch_id',
        'point1': {'x': 'invalid', 'y': 0},
        'point2': {'x': 5, 'y': 0},
        'point3': {'x': 0, 'y': 5}
    }
    
    result = arc_ops.create_arc_by_three_points(params)
    if not result.get('success'):
        logging.info("[PASS] Error handling: Invalid point coordinates correctly rejected")
    else:
        logging.error("[FAIL] Error handling: Should have failed with invalid point coordinates")
        return False
    
    return True

def run_comprehensive_external_test():
    """Run all real external tests with actual ArcOperations class"""
    start_time = datetime.now()
    logging.info("="*60)
    logging.info("STARTING REAL EXTERNAL ARC OPERATIONS TEST WITH ACTUAL CLASS")
    logging.info("="*60)
    
    all_passed = True
    
    try:
        # Test arc creation methods
        result = test_arc_creation_methods_real()
        if not result:
            all_passed = False
        else:
            success, sketch_id, arc1_id, arc2_id, arc3_id = result
            logging.info("[PASS] Arc creation methods completed")
            
            # Test arc query methods
            if test_arc_query_methods_real(sketch_id, arc1_id):
                logging.info("[PASS] Arc query methods completed")
            else:
                all_passed = False
            
            # Test arc manipulation methods (this will modify arc1_id)
            if test_arc_manipulation_methods_real(sketch_id, arc1_id):
                logging.info("[PASS] Arc manipulation methods completed")
            else:
                all_passed = False
        
        # Test error handling
        if test_error_handling_real():
            logging.info("[PASS] Error handling completed")
        else:
            all_passed = False
            
    except Exception as e:
        logging.error(f"[FAIL] Test failed with exception: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        all_passed = False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Generate summary report
    logging.info("="*60)
    logging.info("EXTERNAL TEST SUMMARY REPORT")
    logging.info("="*60)
    logging.info(f"Start time: {start_time}")
    logging.info(f"End time: {end_time}")
    logging.info(f"Duration: {duration}")
    logging.info("")
    
    if all_passed:
        logging.info("[PASS] ALL EXTERNAL TESTS PASSED")
        logging.info("Arc operations are working correctly with real ArcOperations class!")
    else:
        logging.info("[FAIL] SOME EXTERNAL TESTS FAILED")
        logging.info("Check the log for details on what failed.")
    
    logging.info("")
    logging.info("TESTED METHODS WITH REAL CLASS:")
    tested_methods = [
        "create_arc_by_three_points",
        "create_arc_by_center_start_sweep", 
        "create_arc_fillet",
        "get_arc_properties", 
        "get_arc_constraints",
        "get_arc_state",
        "get_arc_intersections",
        "split_arc",
        "break_arc_curve"
    ]
    
    for method in tested_methods:
        logging.info(f"  [TESTED] {method}")
    
    logging.info("")
    logging.info("NOTE: These tests called the real arc_operations.py methods")
    logging.info("directly with enhanced mocks that simulate Fusion 360 API behavior.")
    
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_external_test()
    exit(0 if success else 1)
