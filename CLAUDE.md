# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Fusion 360 add-in that provides Model Context Protocol (MCP) server capabilities for external automation. The codebase is structured as a modular Python add-in with clean separation of concerns:

### Core Components
- **fusion_mcp_addon.py**: Main add-in entry point that initializes all handlers and starts the MCP server
- **fusion_mcp_server.py**: Socket-based MCP server with thread-safe API execution using Fusion's custom events
- **core/**: Document and parameter management operations
- **sketch/**: Complete sketch automation system (management, geometry, constraints)
- **test_direct_sketch.py**: Direct Fusion API testing utilities

### Key Architectural Patterns
1. **Thread Safety**: All Fusion API calls are marshaled to the main UI thread using custom events to prevent crashes
2. **Handler Registration**: Modular handler system where each operation type (document, sketch, etc.) is registered separately
3. **Error Isolation**: Each handler includes comprehensive error handling to prevent add-in crashes
4. **MCP Protocol**: Uses JSON-RPC over TCP sockets on port 8765 for external communication

## Development Commands

### Testing Python Syntax
```bash
python -m py_compile fusion_mcp_addon.py
python -m py_compile fusion_mcp_server.py
```

### Installing in Fusion 360
1. Copy the entire `fusion_addon` directory to Fusion 360's add-ins folder
2. The manifest file `fusion_mcp_addon.manifest` defines the add-in metadata
3. Use Fusion's Add-Ins panel to load and run the add-in

## Critical Implementation Details

### Thread Safety (CRITICAL)
- Fusion API calls from background threads cause crashes
- Use `_execute_on_main_thread()` method which fires custom events
- The `MCPAPICallEventHandler` executes handlers on the main UI thread
- Never call Fusion API directly from socket handler threads

### Handler System
- All MCP methods follow pattern: `fusion.{operation_name}`
- Handlers return standardized JSON responses with success/error states
- Use the `SketchBase` class utilities for common validation and error handling

### Sketch Operations
- Sketches must be in edit mode before adding geometry
- Use `wait_for_operation_complete()` for proper timing with Fusion's compute cycle
- All sketch entities return standardized dictionary representations with IDs

## MCP Server Protocol

The server listens on localhost:8765 and expects JSON-RPC requests:
```json
{
    "method": "fusion.create_line",
    "params": {"sketch_id": "...", "start": {"x": 0, "y": 0}, "end": {"x": 10, "y": 10}},
    "id": 1
}
```

Available method categories:
- **Document**: `fusion.get_document_info`, `fusion.save_document`
- **Parameters**: `fusion.list_parameters`, `fusion.set_parameter`, etc.
- **Sketch Management**: `fusion.create_sketch`, `fusion.activate_sketch`, etc.
- **Sketch Geometry**: `fusion.create_line`, `fusion.create_circle`, etc.
- **Sketch Constraints**: `fusion.add_distance_constraint`, etc.
- **Testing**: `fusion.test_direct_sketch`

## Common Issues

### "Connection Forcibly Closed" 
This indicates a Fusion API crash due to thread safety violations. Ensure all handlers use the main thread execution pattern.

### Sketch Creation Failures
Sketches need proper plane references and must be activated before adding geometry. Use the test handler to isolate issues.

Do NOT use emojis in python files.

When exploring new fusion methods, you must log each step in test files to confirm method and attribute names, and check against web documentation to clarify your thinking.

We cannot see logs added to the addon code, but CAN see logging in our test files.

You cannot move forward without doing so.

To deploy changes, use @deploy_fusion_addon.py and then wait for user confirmation that they've restarted the addon in Fusion

If you add tests, you MUST add them in the test/ directory. Your tests must be conducted outside of Fusion, to test our add on inside.