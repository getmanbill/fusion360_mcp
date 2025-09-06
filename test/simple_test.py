"""
Simple MCP test - basic line creation
"""
import socket
import json
import time

def test_simple_line():
    """Test creating a single line via MCP"""
    try:
        # Connect to MCP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8765))
        print("Connected to Fusion MCP server")
        
        # Create sketch
        sketch_request = {
            "method": "fusion.create_sketch",
            "params": {"plane_reference": "XY"},
            "id": 1
        }
        
        sock.send(json.dumps(sketch_request).encode())
        sketch_response = json.loads(sock.recv(4096).decode())
        print(f"Sketch response: {sketch_response}")
        
        if sketch_response.get('result', {}).get('success'):
            sketch_id = sketch_response['result']['sketch_id']
            print(f"Created sketch: {sketch_id[:20]}...")
            
            time.sleep(2)  # Brief wait
            
            # Create line
            line_request = {
                "method": "fusion.create_line",
                "params": {
                    "sketch_id": sketch_id,
                    "start_point": {"x": 0, "y": 0},
                    "end_point": {"x": 10, "y": 10}
                },
                "id": 2
            }
            
            sock.send(json.dumps(line_request).encode())
            line_response = json.loads(sock.recv(4096).decode())
            print(f"Line response: {line_response}")
            
            if line_response.get('result', {}).get('success'):
                print("SUCCESS: Line created!")
            else:
                print(f"ERROR: Line creation failed")
        else:
            print("ERROR: Sketch creation failed")
        
        sock.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_simple_line()