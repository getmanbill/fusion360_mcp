# Fusion 360 MCP Proof of Concept

A simple proof of concept for communicating with Fusion 360 via Python.

## Quick Test Setup

### 1. Install the Fusion Add-in

1. Open Fusion 360
2. Go to **Tools > Add-Ins > Scripts and Add-Ins**
3. Click the **Add-Ins** tab
4. Click the green **+** button next to "My Add-Ins"
5. Navigate to the `fusion_addon` folder and select it
6. The add-in should appear in the list
7. Select it and click **Run**
8. You should see a message: "Fusion MCP Add-in started! Listening on port 8765"

### 2. Test with Python Client

1. Make sure you have a Fusion document open (any document with some parameters works best)
2. Run the test client:

```bash
python test_fusion_client.py
```

### 3. What It Tests

The test client will:
- ✅ Connect to the running Fusion add-in
- 📋 Get basic document information  
- 📝 List all user parameters in the document
- 🔧 Create a new parameter called "TestParam" 
- ✏️ Modify the parameter value
- 📊 Show the updated parameter list

## Current Capabilities

- **Document Info**: Get document name, path, design type, units
- **List Parameters**: Get all user parameters with names, values, units, expressions
- **Set Parameters**: Create new parameters or modify existing ones

## Next Steps

- Add mesh export functionality
- Add basic CAM operations  
- Add sheet metal operations
- Implement full MCP server protocol
- Add error handling and validation

## Troubleshooting

- **Connection failed**: Make sure Fusion is open and the add-in is running
- **No parameters found**: Create some user parameters in Fusion first (Modify > Parameters)
- **Add-in won't load**: Check the Fusion console for Python errors
