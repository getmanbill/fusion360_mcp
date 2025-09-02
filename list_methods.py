"""
List available MCP methods
"""
import socket
import json

def list_methods():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to MCP server")
        
        # Try a few methods to see what's available
        methods = [
            "fusion.list_sketches",
            "fusion.get_document_info",
            "fusion.create_sketch",
            "fusion.create_line"
        ]
        
        for method in methods:
            request = {
                "method": method,
                "params": {},
                "id": 1
            }
            
            sock.send(json.dumps(request).encode())
            response = json.loads(sock.recv(4096).decode())
            
            if 'error' not in response:
                print(f"Available: {method}")
            else:
                print(f"Not available: {method} - {response.get('error', 'Unknown error')}")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    list_methods()