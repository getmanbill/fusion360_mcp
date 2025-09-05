"""
Direct test of refactored geometry modules - run this from within Fusion 360
This test verifies the geometry module refactoring is working correctly
"""
import adsk.core
import adsk.fusion
import traceback
import json
from datetime import datetime
import os
import sys

def run():
    """Test the refactored geometry modules directly in Fusion 360"""
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Test logging
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "refactored_geometry_direct_test",
            "tests": [],
            "summary": {}
        }
        
        def log_test(name, success, details=""):
            """Log test result"""
            test_results["tests"].append({
                "test": name,
                "success": success,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
            print(f"{'✓' if success else '✗'} {name}: {details}")
        
        print("=" * 60)
        print("TESTING REFACTORED GEOMETRY MODULES IN FUSION 360")
        print("=" * 60)
        
        # Ensure we have an active design
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Please open or create a design first', 'Test Setup')
            return
        
        # Test 1: Import the refactored modules
        try:
            # Import from the deployed addon location
            import sys
            
            # The addon should be in the Fusion scripts directory
            appdata = os.environ.get('APPDATA')
            addon_path = os.path.join(appdata, "Autodesk", "Autodesk Fusion 360", "API", "Scripts", "fusion_mcp_addon")
            if addon_path not in sys.path:
                sys.path.insert(0, addon_path)
            
            from sketch.basic_shapes import BasicShapes
            from sketch.complex_shapes import ComplexShapes  
            from sketch.geometry_utils import GeometryUtils
            from sketch import SketchGeometry  # Backward compatibility
            log_test("Import refactored modules", True, "All modules imported successfully from deployed location")
        except Exception as e:
            log_test("Import refactored modules", False, f"Import failed: {str(e)}")
            ui.messageBox(f'Import failed: {str(e)}', 'Test Error')
            return
        
        # Test 2: Check method availability and inheritance
        try:
            sg = SketchGeometry()
            
            # Test basic shapes methods
            basic_methods = ['create_rectangle', 'create_circle', 'create_line', 'create_arc', 'add_two_point_rectangle']
            basic_ok = all(hasattr(sg, method) for method in basic_methods)
            
            # Test complex shapes methods  
            complex_methods = ['create_polygon', 'create_spline', 'create_ellipse', 'create_slot', 'create_fitted_spline_from_points']
            complex_ok = all(hasattr(sg, method) for method in complex_methods)
            
            # Test utility methods
            util_methods = ['create_point3d', 'create_object_collection', 'create_sketch_with_line', 'get_sketch_revision_id']
            util_ok = all(hasattr(sg, method) for method in util_methods)
            
            # Test base methods
            base_methods = ['validate_point', 'get_sketch_by_id', 'create_point_2d', 'success_response', 'error_response']
            base_ok = all(hasattr(sg, method) for method in base_methods)
            
            if basic_ok and complex_ok and util_ok and base_ok:
                log_test("Method availability", True, f"All methods available: basic={len(basic_methods)}, complex={len(complex_methods)}, util={len(util_methods)}, base={len(base_methods)}")
            else:
                log_test("Method availability", False, f"Missing methods: basic={basic_ok}, complex={complex_ok}, util={util_ok}, base={base_ok}")
        except Exception as e:
            log_test("Method availability", False, f"Error: {str(e)}")
        
        # Test 3: Test individual module instantiation
        try:
            basic = BasicShapes()
            complex_shapes = ComplexShapes()
            utils = GeometryUtils()
            
            # Verify they all have the base functionality
            modules = [('BasicShapes', basic), ('ComplexShapes', complex_shapes), ('GeometryUtils', utils)]
            all_good = True
            
            for name, module in modules:
                has_base = hasattr(module, 'validate_point') and hasattr(module, 'success_response')
                if not has_base:
                    all_good = False
                    break
            
            if all_good:
                log_test("Individual module instantiation", True, "All modules instantiate with base functionality")
            else:
                log_test("Individual module instantiation", False, "Some modules missing base functionality")
        except Exception as e:
            log_test("Individual module instantiation", False, f"Error: {str(e)}")
        
        # Test 4: Create a test sketch for functional testing
        try:
            rootComp = design.rootComponent
            xyPlane = rootComp.xYConstructionPlane
            sketch = rootComp.sketches.add(xyPlane)
            sketch_id = sketch.entityToken
            
            log_test("Create test sketch", True, f"Created sketch: {sketch.name}")
        except Exception as e:
            log_test("Create test sketch", False, f"Error: {str(e)}")
            sketch_id = None
        
        # Test 5: Test basic geometry creation (if we have a sketch)
        if sketch_id:
            try:
                sg = SketchGeometry()
                
                # Test rectangle creation
                rect_params = {
                    'sketch_id': sketch_id,
                    'corner1': {'x': 0, 'y': 0},
                    'corner2': {'x': 10, 'y': 5}
                }
                rect_result = sg.create_rectangle(rect_params)
                rect_success = rect_result.get('success', False)
                
                # Test circle creation
                circle_params = {
                    'sketch_id': sketch_id,
                    'center': {'x': 20, 'y': 10},
                    'radius': 5
                }
                circle_result = sg.create_circle(circle_params)
                circle_success = circle_result.get('success', False)
                
                # Test line creation
                line_params = {
                    'sketch_id': sketch_id,
                    'start_point': {'x': 30, 'y': 0},
                    'end_point': {'x': 40, 'y': 10}
                }
                line_result = sg.create_line(line_params)
                line_success = line_result.get('success', False)
                
                if rect_success and circle_success and line_success:
                    log_test("Basic geometry creation", True, "Rectangle, circle, and line created successfully")
                else:
                    log_test("Basic geometry creation", False, f"Some geometry failed: rect={rect_success}, circle={circle_success}, line={line_success}")
                    
            except Exception as e:
                log_test("Basic geometry creation", False, f"Error: {str(e)}")
        
        # Test 6: Test parameter validation
        try:
            sg = SketchGeometry()
            
            # Test invalid parameters
            invalid_rect = sg.create_rectangle({})  # Missing required params
            invalid_circle = sg.create_circle({'sketch_id': 'invalid'})  # Missing center/radius
            
            rect_validates = not invalid_rect.get('success', True)  # Should fail
            circle_validates = not invalid_circle.get('success', True)  # Should fail
            
            if rect_validates and circle_validates:
                log_test("Parameter validation", True, "Methods properly reject invalid parameters")
            else:
                log_test("Parameter validation", False, f"Validation issues: rect={rect_validates}, circle={circle_validates}")
        except Exception as e:
            log_test("Parameter validation", False, f"Error: {str(e)}")
        
        # Generate summary
        total_tests = len(test_results["tests"])
        passed_tests = sum(1 for test in test_results["tests"] if test["success"])
        test_results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {test_results['summary']['success_rate']}")
        
        # Show results in UI
        if passed_tests == total_tests:
            ui.messageBox(f'🎉 All refactored geometry tests passed!\n\nTotal tests: {total_tests}\nSuccess rate: {test_results["summary"]["success_rate"]}', 'Refactoring Test Success')
        else:
            ui.messageBox(f'⚠️ Some tests failed.\n\nPassed: {passed_tests}/{total_tests}\nSuccess rate: {test_results["summary"]["success_rate"]}\n\nCheck console for details.', 'Refactoring Test Results')
            
    except Exception as e:
        error_msg = f"Test execution failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        if ui:
            ui.messageBox(error_msg, 'Test Error')

# Run the test when script is executed
if __name__ == '__main__':
    run()
else:
    run()
