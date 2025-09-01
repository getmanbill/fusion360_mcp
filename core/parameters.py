"""
Parameter Operations
User parameter creation, modification, and management
"""
import adsk.core
import adsk.fusion
from typing import Dict, Any

class ParameterHandlers:
    """Handles user parameter operations"""
    
    def __init__(self):
        self.app = adsk.core.Application.get()
    
    def list_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all user parameters in the active document"""
        try:
            design = self.app.activeProduct
            if not design or design.objectType != adsk.fusion.Design.classType():
                return {"error": "No active Fusion design"}
                
            user_params = design.userParameters
            parameters = []
            
            # Safe iteration with error handling for each parameter
            try:
                param_count = user_params.count
                for i in range(param_count):
                    try:
                        param = user_params.item(i)
                        if param:  # Make sure param exists
                            parameters.append({
                                "name": param.name if hasattr(param, 'name') else f"param_{i}",
                                "expression": param.expression if hasattr(param, 'expression') else "unknown",
                                "value": param.value if hasattr(param, 'value') else 0.0,
                                "units": param.unit if hasattr(param, 'unit') else "",
                                "comment": param.comment if hasattr(param, 'comment') else ""
                            })
                    except Exception as param_error:
                        # Skip problematic parameters
                        continue
            except Exception as iteration_error:
                return {"error": f"Failed to iterate parameters: {str(iteration_error)}"}
                
            return {
                "parameters": parameters,
                "count": len(parameters)
            }
        except Exception as e:
            return {"error": f"Failed to list parameters: {str(e)}"}

    def set_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a user parameter value"""
        try:
            design = self.app.activeProduct
            if not design or design.objectType != adsk.fusion.Design.classType():
                return {"error": "No active Fusion design"}
                
            param_name = params.get('name')
            param_value = params.get('value')
            param_units = params.get('units', '')
            
            if not param_name or param_value is None:
                return {"error": "Parameter name and value are required"}
                
            user_params = design.userParameters
            
            # Try to find existing parameter
            existing_param = user_params.itemByName(param_name)
            
            if existing_param:
                # Update existing parameter - use proper Fusion expression format
                if param_units:
                    # For units, use the format: "value unit" (e.g., "80 mm", not "80.0 mm")
                    expression = f"{param_value} {param_units}"
                else:
                    expression = str(param_value)
                
                try:
                    existing_param.expression = expression
                    
                    return {
                        "success": True,
                        "parameter": {
                            "name": existing_param.name,
                            "expression": existing_param.expression,
                            "value": existing_param.value,
                            "units": existing_param.unit
                        }
                    }
                except Exception as e:
                    # If direct assignment fails, try just the numeric value
                    try:
                        existing_param.expression = str(param_value)
                        return {
                            "success": True,
                            "parameter": {
                                "name": existing_param.name,
                                "expression": existing_param.expression,
                                "value": existing_param.value,
                                "units": existing_param.unit
                            }
                        }
                    except Exception as e2:
                        return {"error": f"Failed to update parameter: {str(e)} | Also tried: {str(e2)}"}
            else:
                # Create new parameter - use proper Fusion format
                if param_units:
                    # Remove decimal places for cleaner expressions
                    if isinstance(param_value, float) and param_value.is_integer():
                        expression = f"{int(param_value)} {param_units}"
                    else:
                        expression = f"{param_value} {param_units}"
                else:
                    expression = str(param_value)
                    
                # Create ValueInput for the parameter  
                value_input = adsk.core.ValueInput.createByString(expression)
                new_param = user_params.add(param_name, value_input, "", "")
                
                return {
                    "success": True,
                    "parameter": {
                        "name": new_param.name,
                        "expression": new_param.expression,
                        "value": new_param.value,
                        "units": new_param.unit
                    },
                    "created": True
                }
                
        except Exception as e:
            return {"error": f"Failed to set parameter: {str(e)}"}
    
    def delete_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user parameter"""
        try:
            design = self.app.activeProduct
            if not design or design.objectType != adsk.fusion.Design.classType():
                return {"error": "No active Fusion design"}
                
            param_name = params.get('name')
            if not param_name:
                return {"error": "Parameter name is required"}
                
            user_params = design.userParameters
            existing_param = user_params.itemByName(param_name)
            
            if not existing_param:
                return {"error": f"Parameter not found: {param_name}"}
            
            # Delete the parameter
            existing_param.deleteMe()
            
            return {
                "success": True,
                "deleted_parameter": param_name
            }
            
        except Exception as e:
            return {"error": f"Failed to delete parameter: {str(e)}"}
    
    def get_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific parameter"""
        try:
            design = self.app.activeProduct
            if not design or design.objectType != adsk.fusion.Design.classType():
                return {"error": "No active Fusion design"}
                
            param_name = params.get('name')
            if not param_name:
                return {"error": "Parameter name is required"}
                
            user_params = design.userParameters
            existing_param = user_params.itemByName(param_name)
            
            if not existing_param:
                return {"error": f"Parameter not found: {param_name}"}
            
            return {
                "success": True,
                "parameter": {
                    "name": existing_param.name,
                    "expression": existing_param.expression,
                    "value": existing_param.value,
                    "units": existing_param.unit,
                    "comment": existing_param.comment
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get parameter: {str(e)}"}
