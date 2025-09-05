"""
Quick debug test to see if basic line creation still works
"""
import socket
import json

def debug_line_response():
    """Debug what create_line is returning to compare"""
    try:
        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect(('localhost', 8765))
        
        # Create document
        request = {
            "method": "fusion.new_document",
            "params": {"document_type": "FusionDesignDocumentType"},
            "id": 1
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        
        # Create sketch
        request = {
            "method": "fusion.create_sketch",
            "params": {"plane_reference": "XY", "name": "LineDebugSketch"},
            "id": 2
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sketch_response = json.loads(response)
        sketch_id = sketch_response.get('result', {}).get('sketch_id')
        print("📐 Sketch created for line test")
        
        # Test line creation
        request = {
            "method": "fusion.create_line",
            "params": {
                "sketch_id": sketch_id,
                "start_point": {"x": 0, "y": 0},
                "end_point": {"x": 10, "y": 10}
            },
            "id": 3
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        line_response = json.loads(response)
        print("\n📏 Line creation response:")
        print(json.dumps(line_response, indent=2))
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_line_response()
