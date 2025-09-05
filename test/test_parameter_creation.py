"""
Test Parameter Creation
Simple test to check if parameter creation is working correctly
"""
import socket
import json

class ParameterTester:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def send_request(self, method: str, params: dict = None):
        if params is None:
            params = {}
            
        request = {
            "method": method,
            "params": params,
            "id": self.request_id
        }
        
        self.request_id += 1
        
        try:
            request_json = json.dumps(request) + '\n'
            self.socket.send(request_json.encode('utf-8'))
            
            response_data = self.socket.recv(8192).decode('utf-8')
            response = json.loads(response_data)
            
            return response
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def close(self):
        if self.socket:
            self.socket.close()

def test_parameter_formats():
    """Test different parameter formats to see which work"""
    tester = ParameterTester()
    
    if not tester.connect():
        return
        
    try:
        # Create new document
        print("Creating new document...")
        result = tester.send_request('fusion.new_document', {
            'document_type': 'FusionDesignDocumentType'
        })
        print(f"Document creation: {result}")
        
        # Test different parameter formats
        test_params = [
            {"name": "test_simple", "value": 100},  # No units
            {"name": "test_with_units", "value": 120, "units": "mm"},  # Separate units
            {"name": "test_string_expr", "value": "150 mm"},  # String expression
            {"name": "test_float", "value": 25.5, "units": "mm"},  # Float with units
        ]
        
        print("\nTesting parameter creation formats:")
        print("-" * 50)
        
        for param in test_params:
            print(f"\nTesting: {param}")
            result = tester.send_request('fusion.set_parameter', param)
            
            if 'error' in result:
                print(f"  ❌ FAILED: {result['error']}")
            else:
                param_info = result.get('result', {}).get('parameter', {})
                name = param_info.get('name', 'UNKNOWN')
                expression = param_info.get('expression', 'UNKNOWN')
                value = param_info.get('value', 'UNKNOWN')
                units = param_info.get('units', 'UNKNOWN')
                
                print(f"  ✅ SUCCESS:")
                print(f"     Name: {name}")
                print(f"     Expression: {expression}")
                print(f"     Value: {value}")
                print(f"     Units: {units}")
        
        # List all parameters to see what was created
        print(f"\nListing all parameters:")
        print("-" * 50)
        result = tester.send_request('fusion.list_parameters')
        
        if 'error' not in result:
            params = result.get('result', {}).get('parameters', [])
            for param in params:
                print(f"  {param}")
        else:
            print(f"  Failed to list parameters: {result['error']}")
            
    finally:
        tester.close()

if __name__ == "__main__":
    test_parameter_formats()
