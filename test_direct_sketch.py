"""
Direct sketch test - bypasses MCP to test if sketch creation works at all
This helps isolate whether the issue is with MCP or Fusion itself
"""
import adsk.core
import adsk.fusion

def test_direct_sketch():
    """Test creating a sketch directly without MCP"""
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    try:
        # Get design
        design = app.activeProduct
        if not design or design.objectType != adsk.fusion.Design.classType():
            ui.messageBox("No active design!", "Error")
            return
        
        # Get root component and create sketch
        root = design.rootComponent
        xyPlane = root.xYConstructionPlane
        sketch = root.sketches.add(xyPlane)
        
        # Try to create a line
        try:
            pt1 = adsk.core.Point3D.create(0, 0, 0)
            pt2 = adsk.core.Point3D.create(10, 10, 0)
            
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(pt1, pt2)
            ui.messageBox("✅ Line created successfully!", "SUCCESS")
            
        except Exception as e:
            ui.messageBox(f"❌ Line creation failed: {str(e)}", "FAILED")
            
    except Exception as e:
        ui.messageBox(f"Test failed: {str(e)}", "Test Failed")

# Add this function to be callable from the handlers
def run_test(params=None):
    """Run the direct test"""
    test_direct_sketch()
    return {"success": True, "message": "Direct test completed"}





