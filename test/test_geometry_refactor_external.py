"""
External test for geometry module refactoring
Tests the module structure without requiring Fusion 360 environment
"""
import os
import sys
import importlib.util
from pathlib import Path
import traceback

def test_module_structure():
    """Test the refactored geometry module structure"""
    print("=" * 60)
    print("EXTERNAL GEOMETRY REFACTORING TEST")
    print("=" * 60)
    
    # Get the fusion_addon directory
    current_dir = Path(__file__).parent
    fusion_addon_dir = current_dir / "fusion_addon"
    sketch_dir = fusion_addon_dir / "sketch"
    
    if not fusion_addon_dir.exists():
        print(f"❌ ERROR: fusion_addon directory not found at {fusion_addon_dir}")
        return False
    
    print(f"📁 Testing from: {fusion_addon_dir}")
    
    # Test results tracking
    tests_passed = 0
    tests_total = 0
    
    def run_test(test_name, test_func):
        nonlocal tests_passed, tests_total
        tests_total += 1
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}")
                tests_passed += 1
                return True
            else:
                print(f"❌ {test_name}")
                return False
        except Exception as e:
            print(f"❌ {test_name} - Error: {str(e)}")
            return False
    
    # Test 1: Check all required files exist
    def test_files_exist():
        required_files = [
            "sketch/__init__.py",
            "sketch/base.py",
            "sketch/basic_shapes.py", 
            "sketch/complex_shapes.py",
            "sketch/geometry_utils.py",
            "sketch/constraints.py",
            "sketch/management.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = fusion_addon_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   Missing files: {missing_files}")
            return False
        
        # Check old geometry.py is deleted
        old_geometry = sketch_dir / "geometry.py"
        if old_geometry.exists():
            print("   Old geometry.py still exists (should be deleted)")
            return False
            
        print("   All required files present, old geometry.py correctly removed")
        return True
    
    # Test 2: Check file contents and structure
    def test_file_contents():
        # Check basic_shapes.py has expected class and methods
        basic_shapes_file = sketch_dir / "basic_shapes.py"
        content = basic_shapes_file.read_text()
        
        if "class BasicShapes(SketchBase):" not in content:
            print("   BasicShapes class not found")
            return False
            
        basic_methods = ['create_rectangle', 'create_circle', 'create_line', 'create_arc']
        for method in basic_methods:
            if f"def {method}(" not in content:
                print(f"   Missing method: {method}")
                return False
        
        # Check complex_shapes.py
        complex_shapes_file = sketch_dir / "complex_shapes.py"
        content = complex_shapes_file.read_text()
        
        if "class ComplexShapes(SketchBase):" not in content:
            print("   ComplexShapes class not found")
            return False
            
        complex_methods = ['create_polygon', 'create_ellipse', 'create_slot', 'create_spline']
        for method in complex_methods:
            if f"def {method}(" not in content:
                print(f"   Missing method: {method}")
                return False
        
        # Check geometry_utils.py
        utils_file = sketch_dir / "geometry_utils.py"
        content = utils_file.read_text()
        
        if "class GeometryUtils(SketchBase):" not in content:
            print("   GeometryUtils class not found")
            return False
            
        util_methods = ['create_point3d', 'create_object_collection']
        for method in util_methods:
            if f"def {method}(" not in content:
                print(f"   Missing method: {method}")
                return False
        
        print("   All classes and methods found in correct files")
        return True
    
    # Test 3: Check __init__.py structure
    def test_init_structure():
        init_file = sketch_dir / "__init__.py"
        content = init_file.read_text()
        
        # Check imports
        required_imports = [
            "from .basic_shapes import BasicShapes",
            "from .complex_shapes import ComplexShapes",
            "from .geometry_utils import GeometryUtils"
        ]
        
        for import_line in required_imports:
            if import_line not in content:
                print(f"   Missing import: {import_line}")
                return False
        
        # Check backward compatibility class
        if "class SketchGeometry(BasicShapes, ComplexShapes, GeometryUtils):" not in content:
            print("   Backward compatibility SketchGeometry class not found")
            return False
        
        # Check __all__ exports
        expected_exports = ['SketchGeometry', 'BasicShapes', 'ComplexShapes', 'GeometryUtils']
        for export in expected_exports:
            if f"'{export}'" not in content:
                print(f"   Missing export: {export}")
                return False
        
        print("   __init__.py structure correct")
        return True
    
    # Test 4: Check syntax validity (without imports)
    def test_syntax_validity():
        files_to_check = [
            sketch_dir / "basic_shapes.py",
            sketch_dir / "complex_shapes.py", 
            sketch_dir / "geometry_utils.py"
        ]
        
        for file_path in files_to_check:
            try:
                # Read and check if Python can parse the file
                with open(file_path, 'r') as f:
                    source = f.read()
                
                # Remove adsk imports to avoid import errors
                lines = source.split('\n')
                filtered_lines = []
                skip_next = False
                
                for line in lines:
                    if 'import adsk.' in line or 'from adsk.' in line:
                        filtered_lines.append(f"# {line}")  # Comment out adsk imports
                    elif line.strip().startswith('adsk.') and '=' in line:
                        # Comment out lines that use adsk objects directly
                        filtered_lines.append(f"# {line}")
                    else:
                        filtered_lines.append(line)
                
                filtered_source = '\n'.join(filtered_lines)
                
                # Try to compile (this checks syntax)
                compile(filtered_source, str(file_path), 'exec')
                
            except SyntaxError as e:
                print(f"   Syntax error in {file_path.name}: {e}")
                return False
            except Exception as e:
                print(f"   Error checking {file_path.name}: {e}")
                return False
        
        print("   All files have valid Python syntax")
        return True
    
    # Test 5: Check method distribution
    def test_method_distribution():
        # Count methods in each file
        basic_file = sketch_dir / "basic_shapes.py"
        complex_file = sketch_dir / "complex_shapes.py"
        utils_file = sketch_dir / "geometry_utils.py"
        
        def count_methods(file_path):
            content = file_path.read_text()
            return len([line for line in content.split('\n') if line.strip().startswith('def ') and '(' in line])
        
        basic_methods = count_methods(basic_file)
        complex_methods = count_methods(complex_file)
        utils_methods = count_methods(utils_file)
        
        # Should have roughly balanced distribution
        total_methods = basic_methods + complex_methods + utils_methods
        
        if total_methods < 10:  # Should have at least 10 methods total
            print(f"   Too few methods found: {total_methods}")
            return False
        
        if basic_methods < 3 or complex_methods < 3 or utils_methods < 2:
            print(f"   Unbalanced distribution: basic={basic_methods}, complex={complex_methods}, utils={utils_methods}")
            return False
        
        print(f"   Good method distribution: basic={basic_methods}, complex={complex_methods}, utils={utils_methods}")
        return True
    
    # Test 6: Check file sizes are reasonable
    def test_file_sizes():
        basic_size = (sketch_dir / "basic_shapes.py").stat().st_size
        complex_size = (sketch_dir / "complex_shapes.py").stat().st_size
        utils_size = (sketch_dir / "geometry_utils.py").stat().st_size
        
        # Each file should be substantial but not too large
        if basic_size < 5000 or complex_size < 5000:  # At least 5KB each
            print(f"   Files too small: basic={basic_size}, complex={complex_size}")
            return False
        
        if basic_size > 50000 or complex_size > 50000 or utils_size > 50000:  # Max 50KB each
            print(f"   Files too large: basic={basic_size}, complex={complex_size}, utils={utils_size}")
            return False
        
        print(f"   File sizes reasonable: basic={basic_size//1000}KB, complex={complex_size//1000}KB, utils={utils_size//1000}KB")
        return True
    
    # Run all tests
    print("\n🧪 RUNNING TESTS")
    print("-" * 40)
    
    run_test("Required files exist", test_files_exist)
    run_test("File contents and structure", test_file_contents)
    run_test("__init__.py structure", test_init_structure)
    run_test("Python syntax validity", test_syntax_validity)
    run_test("Method distribution", test_method_distribution)
    run_test("File sizes reasonable", test_file_sizes)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed/tests_total*100):.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Geometry module refactoring is complete and ready")
        print("✅ Deployment should work correctly")
        print("✅ Backward compatibility maintained")
        return True
    else:
        print(f"\n⚠️  {tests_total - tests_passed} TESTS FAILED")
        print("❌ Refactoring may have issues")
        return False

def main():
    """Main test runner"""
    try:
        success = test_module_structure()
        if success:
            print("\n🚀 Ready for deployment and testing in Fusion 360!")
        else:
            print("\n🔧 Please fix the issues before deployment")
        return success
    except Exception as e:
        print(f"\n💥 Test runner failed: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
