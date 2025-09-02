"""
Test the direct sketch test via MCP
"""
import socket
import json

def test_direct_via_mcp():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to MCP server")
        
        # Test the direct sketch function
        request = {
            "method": "fusion.test_direct_sketch", 
            "params": {},
            "id": 1
        }
        
        sock.send(json.dumps(request).encode())
        response = json.loads(sock.recv(4096).decode())
        
        print(f"Direct test response: {response}")
        
        if response.get('result', {}).get('success'):
            print("SUCCESS: Direct test worked!")
        else:
            print("ERROR: Direct test failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_direct_via_mcp()