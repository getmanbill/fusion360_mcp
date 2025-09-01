"""
Direct Fusion 360 test - run this in Fusion's Scripts and Add-Ins
Copy and paste this code into a new script in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Get active design
        design = app.activeProduct
        if not design or design.objectType != adsk.fusion.Design.classType():
            ui.messageBox("No active design!", "Error")
            return
        
        # Get root component
        rootComp = design.rootComponent
        
        # Create sketch on XY plane
        xyPlane = rootComp.xYConstructionPlane
        sketch = rootComp.sketches.add(xyPlane)
        ui.messageBox(f"Sketch created: {sketch.name}", "Success")
        
        # Test 1: Basic line (from official sample)
        try:
            pt1 = adsk.core.Point3D.create(0, 0, 0)
            pt2 = adsk.core.Point3D.create(10, 10, 0)
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(pt1, pt2)
            ui.messageBox("SUCCESS: Basic line created!", "Test 1")
        except Exception as e:
            ui.messageBox(f"FAILED: Basic line: {str(e)}", "Test 1")
        
        # Test 2: Rectangle (from official sample)
        try:
            rect_lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(15, 0, 0), 
                adsk.core.Point3D.create(25, 10, 0)
            )
            ui.messageBox("SUCCESS: Rectangle created!", "Test 2")
        except Exception as e:
            ui.messageBox(f"FAILED: Rectangle: {str(e)}", "Test 2")
        
        # Test 3: Circle
        try:
            center = adsk.core.Point3D.create(30, 5, 0)
            circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, 5)
            ui.messageBox("SUCCESS: Circle created!", "Test 3")
        except Exception as e:
            ui.messageBox(f"FAILED: Circle: {str(e)}", "Test 3")
            
    except:
        if ui:
            ui.messageBox(f'Script failed: {traceback.format_exc()}', "Error")