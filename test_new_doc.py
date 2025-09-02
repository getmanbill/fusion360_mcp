"""
Test new document sketch creation
"""
import socket
import json

def test_new_doc():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to MCP server")
        
        # Test new document sketch creation
        request = {
            "method": "fusion.test_new_doc_sketch", 
            "params": {},
            "id": 1
        }
        
        sock.send(json.dumps(request).encode())
        response = json.loads(sock.recv(4096).decode())
        
        print(f"New doc test response: {response}")
        
        if response.get('result', {}).get('success'):
            print("SUCCESS: New document line creation worked!")
        else:
            print("ERROR: New document test failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_new_doc()