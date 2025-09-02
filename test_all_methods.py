"""
Test all available methods
"""
import socket
import json

def test_all_methods():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to MCP server")
        
        # Try all possible test methods
        test_methods = [
            "fusion.test_direct_sketch",
            "fusion.test_new_doc_sketch"
        ]
        
        for method in test_methods:
            print(f"\nTesting: {method}")
            request = {
                "method": method,
                "params": {},
                "id": 1
            }
            
            sock.send(json.dumps(request).encode())
            response = json.loads(sock.recv(4096).decode())
            
            if 'error' not in response:
                print(f"SUCCESS: {method} worked!")
                print(f"Response: {response}")
            else:
                print(f"ERROR: {method} - {response.get('error', 'Unknown')}")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_all_methods()