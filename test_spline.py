"""
Test spline creation
"""
import socket
import json

def test_spline():
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
            
            # Create spline with 4 points
            spline_request = {
                "method": "fusion.create_spline",
                "params": {
                    "sketch_id": sketch_id,
                    "points": [
                        {"x": 0, "y": 0},
                        {"x": 10, "y": 15},
                        {"x": 25, "y": 10},
                        {"x": 35, "y": 20}
                    ]
                },
                "id": 2
            }
            
            sock.send(json.dumps(spline_request).encode())
            spline_response = json.loads(sock.recv(4096).decode())
            print(f"Spline response: {spline_response}")
            
            if spline_response.get('result', {}).get('success'):
                print("SUCCESS: Spline created!")
            else:
                print("ERROR: Spline creation failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_spline()