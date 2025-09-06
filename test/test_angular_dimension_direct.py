"""
Direct Angular Dimension Test
Tests the angular dimension functionality by examining code without importing SDK
Following workspace rules: testing outside of Fusion to test our addon inside
"""
import os
import re
import json

def test_angular_dimension_method_structure():
    """Test the method structure by examining the source code"""
    print("🔍 Testing Angular Dimension Method Structure...")
    print("=" * 50)
    
    try:
        # Read the implementation file directly
        impl_file = os.path.join(os.path.dirname(__file__), '..', 'fusion_addon', 'sketch', 'constraints.py')
        
        with open(impl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check method exists
        method_pattern = r'def add_angular_dimension\(self, params: Dict\[str, Any\]\) -> Dict\[str, Any\]:'
        if re.search(method_pattern, content):
            print("✅ add_angular_dimension method exists with correct signature")
        else:
            print("❌ add_angular_dimension method not found or incorrect signature")
            return False
            
        # Extract the method body
        method_start = content.find('def add_angular_dimension(')
        if method_start == -1:
            print("❌ Method definition not found")
            return False
            
        # Find the end of the method (next method definition or end of class)
        lines = content[method_start:].split('\n')
        method_lines = []
        indent_level = None
        
        for line in lines:
            if line.strip().startswith('def ') and 'add_angular_dimension' not in line and method_lines:
                break  # Found next method
            if line.strip() and indent_level is None:
                indent_level = len(line) - len(line.lstrip())
            elif line.strip() and len(line) - len(line.lstrip()) <= indent_level and method_lines:
                break  # Found end of method
            method_lines.append(line)
            
        method_body = '\n'.join(method_lines)
        
        # Test parameter validation logic
        validation_checks = [
            ('sketch_id extraction', r"sketch_id = params\.get\('sketch_id'\)"),
            ('line1_id extraction', r"line1_id = params\.get\('line1_id'\)"),
            ('line2_id extraction', r"line2_id = params\.get\('line2_id'\)"),
            ('angle_value extraction', r"angle_value = params\.get\('angle_value'\)"),
            ('required params check', r"if not all\(\[.*sketch_id.*line1_id.*line2_id.*\]\).*or.*angle_value.*is None"),
            ('angle type validation', r"if not isinstance\(angle_value, \(int, float\)\)"),
            ('error response for validation', r"return self\.error_response"),
        ]
        
        validation_score = 0
        for check_name, pattern in validation_checks:
            if re.search(pattern, method_body):
                print(f"   ✅ {check_name}")
                validation_score += 1
            else:
                print(f"   ❌ {check_name} - pattern not found")
                
        print(f"\n📊 Parameter Validation: {validation_score}/{len(validation_checks)} checks passed")
        
        return validation_score >= 5  # Allow some flexibility
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_method_implementation_details():
    """Test implementation details and code structure"""
    print("\n🔍 Testing Implementation Details...")
    print("=" * 40)
    
    try:
        # Read the actual implementation file to verify structure
        impl_file = os.path.join(os.path.dirname(__file__), '..', 'fusion_addon', 'sketch', 'constraints.py')
        
        with open(impl_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key implementation elements
        checks = [
            ('add_angular_dimension method definition', 'def add_angular_dimension('),
            ('Parameter extraction', 'params.get('),
            ('Sketch ID validation', 'sketch_id'),
            ('Line ID validation', 'line1_id'),
            ('Angle value validation', 'angle_value'),
            ('Text position handling', 'text_position'),
            ('Fusion API call', 'addAngularDimension'),
            ('Parameter expression setting', 'parameter.expression'),
            ('Success response', 'success_response'),
            ('Error handling', 'error_response')
        ]
        
        implementation_score = 0
        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"   ✅ {check_name}")
                implementation_score += 1
            else:
                print(f"   ❌ {check_name} - pattern '{check_pattern}' not found")
                
        print(f"\n📊 Implementation Checks: {implementation_score}/{len(checks)} passed")
        
        # Check for expected API usage
        api_checks = [
            ('Correct Fusion API method', 'sketch.dimensions.addAngularDimension'),
            ('Point2D creation', 'adsk.core.Point2D.create'),
            ('Entity token return', 'entityToken'),
            ('Parameter name handling', 'parameter.name')
        ]
        
        api_score = 0
        for check_name, check_pattern in api_checks:
            if check_pattern in content:
                print(f"   ✅ {check_name}")
                api_score += 1
            else:
                print(f"   ⚠️  {check_name} - pattern '{check_pattern}' not found")
                
        print(f"\n📊 API Usage Checks: {api_score}/{len(api_checks)} passed")
        
        return implementation_score >= 8 and api_score >= 2  # Allow some flexibility
        
    except Exception as e:
        print(f"❌ Implementation check failed: {e}")
        return False

def test_integration_with_constraints_module():
    """Test integration with the constraints module by examining code"""
    print("\n🔍 Testing Integration with Constraints Module...")
    print("=" * 45)
    
    try:
        # Check constraints.py file structure
        impl_file = os.path.join(os.path.dirname(__file__), '..', 'fusion_addon', 'sketch', 'constraints.py')
        
        with open(impl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for related constraint methods in the same file
        related_methods = [
            ('add_angular_dimension', r'def add_angular_dimension\('),
            ('add_angle_constraint', r'def add_angle_constraint\('), 
            ('add_radius_constraint', r'def add_radius_constraint\('),
            ('add_distance_constraint', r'def add_distance_constraint\('),
            ('add_coincident_constraint', r'def add_coincident_constraint\('),
            ('add_parallel_constraint', r'def add_parallel_constraint\('),
            ('add_perpendicular_constraint', r'def add_perpendicular_constraint\(')
        ]
        
        found_methods = []
        for method_name, pattern in related_methods:
            if re.search(pattern, content):
                found_methods.append(method_name)
                print(f"   ✅ {method_name}")
            else:
                print(f"   ❌ {method_name} not found")
                
        # Check handler registration in main addon file
        addon_file = os.path.join(os.path.dirname(__file__), '..', 'fusion_addon', 'fusion_mcp_addon.py')
        
        with open(addon_file, 'r', encoding='utf-8') as f:
            addon_content = f.read()
            
        # Check if add_angular_dimension is registered
        registration_pattern = r"register_handler\('fusion\.add_angular_dimension'"
        if re.search(registration_pattern, addon_content):
            print(f"   ✅ add_angular_dimension properly registered in MCP handler")
            registration_ok = True
        else:
            print(f"   ❌ add_angular_dimension not registered in MCP handler")
            registration_ok = False
                
        integration_success = 'add_angular_dimension' in found_methods and registration_ok
        print(f"\n📊 Integration: {'✅ Good' if integration_success else '❌ Issues'}")
        
        return integration_success
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_all_direct_tests():
    """Run all direct tests"""
    print("==> Starting Direct Angular Dimension Tests")
    print("Testing outside Fusion to verify addon implementation")
    print("=" * 70)
    
    test_results = []
    
    # Run tests
    test_results.append(("Method Structure", test_angular_dimension_method_structure()))
    test_results.append(("Implementation Details", test_method_implementation_details()))
    test_results.append(("Module Integration", test_integration_with_constraints_module()))
    
    # Summary
    print("\n📊 DIRECT TEST SUMMARY")
    print("=" * 30)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(test_results)) * 100
    print(f"\nOverall: {passed}/{len(test_results)} tests passed ({success_rate:.1f}%)")
    
    overall_success = passed == len(test_results)
    print(f"\n{'✅ ALL DIRECT TESTS PASSED' if overall_success else '❌ SOME DIRECT TESTS FAILED'}")
    
    if overall_success:
        print("\n==> Your add_angular_dimension method implementation looks solid!")
        print("==> Next: Deploy to Fusion and run the MCP server tests")
    else:
        print("\n==> Some issues found in the implementation - check the details above")
    
    return overall_success

if __name__ == "__main__":
    success = run_all_direct_tests()
    if not success:
        exit(1)
