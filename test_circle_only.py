"""
Test circle creation only
"""
import socket
import json

def test_circle():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to MCP server")
        
        # Create sketch
        sketch_request = {
            "method": "fusion.create_sketch",
            "params": {"plane_reference": "XY"},
            "id": 1
        }
        
        sock.send(json.dumps(sketch_request).encode())
        sketch_response = json.loads(sock.recv(4096).decode())
        
        if sketch_response.get('result', {}).get('success'):
            sketch_id = sketch_response['result']['sketch_id']
            print(f"Sketch created: {sketch_id[:20]}...")
            
            # Test circle creation (different API than lines)
            circle_request = {
                "method": "fusion.create_circle",
                "params": {
                    "sketch_id": sketch_id,
                    "center": {"x": 10, "y": 10},
                    "radius": 5
                },
                "id": 2
            }
            
            sock.send(json.dumps(circle_request).encode())
            circle_response = json.loads(sock.recv(4096).decode())
            print(f"Circle response: {circle_response}")
            
            if circle_response.get('result', {}).get('success'):
                print("SUCCESS: Circle created!")
            else:
                print("ERROR: Circle creation failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_circle()