"""
Fusion 360 MCP Add-in (Modular Version)
Clean, organized version with separated concerns
"""
import adsk.core
import traceback
from .fusion_mcp_server import MCPServer
from .core import DocumentHandlers, ParameterHandlers
from .sketch import SketchManagement, SketchGeometry, SketchConstraints

# Global variables
app = adsk.core.Application.get()
ui = app.userInterface
mcp_server = None
handlers = {}

def run(context):
    """Main entry point for the add-in"""
    global mcp_server, handlers
    
    try:
        # Initialize components
        mcp_server = MCPServer()
        
        # Initialize all handler modules
        handlers['document'] = DocumentHandlers()
        handlers['parameters'] = ParameterHandlers()
        handlers['sketch_mgmt'] = SketchManagement()
        handlers['sketch_geom'] = SketchGeometry()
        handlers['sketch_constraints'] = SketchConstraints()
        
        # Register document handlers
        mcp_server.register_handler('fusion.get_document_info', handlers['document'].get_document_info)
        mcp_server.register_handler('fusion.open_document', handlers['document'].open_document)
        mcp_server.register_handler('fusion.save_document', handlers['document'].save_document)
        
        # Register parameter handlers
        mcp_server.register_handler('fusion.list_parameters', handlers['parameters'].list_parameters)
        mcp_server.register_handler('fusion.set_parameter', handlers['parameters'].set_parameter)
        mcp_server.register_handler('fusion.get_parameter', handlers['parameters'].get_parameter)
        mcp_server.register_handler('fusion.delete_parameter', handlers['parameters'].delete_parameter)
        
        # Register sketch management handlers
        mcp_server.register_handler('fusion.create_sketch', handlers['sketch_mgmt'].create_sketch)
        mcp_server.register_handler('fusion.list_sketches', handlers['sketch_mgmt'].list_sketches)
        mcp_server.register_handler('fusion.activate_sketch', handlers['sketch_mgmt'].activate_sketch)
        mcp_server.register_handler('fusion.finish_sketch', handlers['sketch_mgmt'].finish_sketch)
        mcp_server.register_handler('fusion.get_sketch_info', handlers['sketch_mgmt'].get_sketch_info)
        mcp_server.register_handler('fusion.delete_sketch', handlers['sketch_mgmt'].delete_sketch)
        
        # Register sketch geometry handlers
        mcp_server.register_handler('fusion.create_rectangle', handlers['sketch_geom'].create_rectangle)
        mcp_server.register_handler('fusion.create_circle', handlers['sketch_geom'].create_circle)
        mcp_server.register_handler('fusion.create_line', handlers['sketch_geom'].create_line)
        mcp_server.register_handler('fusion.create_arc', handlers['sketch_geom'].create_arc)
        mcp_server.register_handler('fusion.create_polygon', handlers['sketch_geom'].create_polygon)
        mcp_server.register_handler('fusion.create_spline', handlers['sketch_geom'].create_spline)
        mcp_server.register_handler('fusion.create_sketch_with_line', handlers['sketch_geom'].create_sketch_with_line)
        
        # Register sketch constraint handlers
        mcp_server.register_handler('fusion.add_coincident_constraint', handlers['sketch_constraints'].add_coincident_constraint)
        mcp_server.register_handler('fusion.add_distance_constraint', handlers['sketch_constraints'].add_distance_constraint)
        mcp_server.register_handler('fusion.add_parallel_constraint', handlers['sketch_constraints'].add_parallel_constraint)
        mcp_server.register_handler('fusion.add_perpendicular_constraint', handlers['sketch_constraints'].add_perpendicular_constraint)
        mcp_server.register_handler('fusion.add_radius_constraint', handlers['sketch_constraints'].add_radius_constraint)
        mcp_server.register_handler('fusion.add_angle_constraint', handlers['sketch_constraints'].add_angle_constraint)
        
        
        # Log all registered handlers
        handler_list = list(mcp_server.handlers.keys())
        ui.messageBox(f'Total handlers registered: {len(handler_list)}\n{", ".join(handler_list)}', 'All Handlers')
        
        # Start the server
        ui.messageBox('Starting MCP server...', 'Server Start')
        mcp_server.start()
        ui.messageBox('MCP server started successfully!', 'Server Start')
        
        ui.messageBox('Fusion MCP Add-in (v2) started!\nListening on port 8765\n\nHandlers available:\n- fusion.test_direct_sketch\n- fusion.create_line\n- fusion.create_sketch')
        
    except Exception as e:
        error_msg = f'Failed to start add-in: {str(e)}\n{traceback.format_exc()}'
        ui.messageBox(error_msg)
        

def stop(context):
    """Clean up when add-in is stopped"""
    global mcp_server
    
    try:
        if mcp_server:
            mcp_server.stop()
        ui.messageBox('Fusion MCP Add-in (v2) stopped')
    except Exception as e:
        ui.messageBox(f'Error stopping add-in: {str(e)}')
