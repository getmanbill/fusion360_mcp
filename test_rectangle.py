"""
Test rectangle creation (uses different API)
"""
import socket
import json

def test_rectangle():
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
        print(f"Sketch created: {sketch_response.get('result', {}).get('success', False)}")
        
        if sketch_response.get('result', {}).get('success'):
            sketch_id = sketch_response['result']['sketch_id']
            
            # Test rectangle (uses addTwoPointRectangle)
            rect_request = {
                "method": "fusion.create_rectangle",
                "params": {
                    "sketch_id": sketch_id,
                    "corner1": {"x": 0, "y": 0},
                    "corner2": {"x": 20, "y": 15}
                },
                "id": 2
            }
            
            sock.send(json.dumps(rect_request).encode())
            rect_response = json.loads(sock.recv(4096).decode())
            print(f"Rectangle response: {rect_response}")
            
            if rect_response.get('result', {}).get('success'):
                print("SUCCESS: Rectangle created!")
            else:
                print("ERROR: Rectangle creation failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_rectangle()