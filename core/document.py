"""
Document Operations
Basic document information and management
"""
import adsk.core
import adsk.fusion
from typing import Dict, Any

class DocumentHandlers:
    """Handles document-level operations"""
    
    def __init__(self):
        self.app = adsk.core.Application.get()
    
    def get_document_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get basic information about the active document"""
        try:
            design = self.app.activeProduct
            if not design or design.objectType != adsk.fusion.Design.classType():
                return {"error": "No active Fusion design"}
                
            doc = self.app.activeDocument
            
            return {
                "document_name": doc.name,
                "document_path": doc.dataFile.parentFolder.name if doc.dataFile else "Unsaved",
                "design_type": design.designType,
                "units": design.unitsManager.defaultLengthUnits
            }
        except Exception as e:
            return {"error": f"Failed to get document info: {str(e)}"}
    
    def open_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open a Fusion 360 document"""
        try:
            file_path = params.get('path')
            if not file_path:
                return {"error": "path parameter is required"}
            
            # TODO: Implement document opening
            # This requires working with Fusion's data API
            return {"error": "Document opening not yet implemented"}
            
        except Exception as e:
            return {"error": f"Failed to open document: {str(e)}"}
    
    def save_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save the active document - SAFE VERSION"""
        try:
            doc = self.app.activeDocument
            if not doc:
                return {"error": "No active document"}
            
            # Check if document can be saved
            if not doc.dataFile:
                return {"error": "Document must be saved with saveAs first (unsaved document)"}
            
            if doc.isModified:
                # Only save if document is actually modified
                try:
                    doc.save("MCP Auto Save")
                    return {
                        "success": True,
                        "document_name": doc.name,
                        "saved": True
                    }
                except Exception as save_error:
                    return {"error": f"Save failed: {str(save_error)}"}
            else:
                return {
                    "success": True,
                    "document_name": doc.name,
                    "saved": False,
                    "message": "No changes to save"
                }
            
        except Exception as e:
            return {"error": f"Failed to save document: {str(e)}"}
    
    def new_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        try:
            # TODO: Implement new document creation
            return {"error": "New document creation not yet implemented"}
            
        except Exception as e:
            return {"error": f"Failed to create new document: {str(e)}"}
