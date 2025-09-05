"""
Quick debug test to verify ellipse still works for comparison
"""
import socket
import json

def debug_ellipse_response():
    """Debug what create_ellipse is returning to compare with slot"""
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
            "params": {"plane_reference": "XY", "name": "EllipseDebugSketch"},
            "id": 2
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sketch_response = json.loads(response)
        sketch_id = sketch_response.get('result', {}).get('sketch_id')
        print("📐 Sketch created for ellipse test")
        
        # Test ellipse creation
        ellipse_params = {
            "sketch_id": sketch_id,
            "center": {"x": 0, "y": 0},
            "major_axis": 10,
            "minor_axis": 5
        }
        
        print(f"\n🔵 Testing ellipse with parameters:")
        print(f"   sketch_id: {sketch_id}")
        print(f"   center: {ellipse_params['center']}")
        print(f"   major_axis: {ellipse_params['major_axis']}")
        print(f"   minor_axis: {ellipse_params['minor_axis']}")
        
        request = {
            "method": "fusion.create_ellipse",
            "params": ellipse_params,
            "id": 3
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        ellipse_response = json.loads(response)
        print("\n🔵 Ellipse creation response:")
        print(json.dumps(ellipse_response, indent=2))
        
        # Test with different parameter combinations
        print("\n🧪 Testing ellipse with rotation parameter:")
        ellipse_params_rotation = {
            "sketch_id": sketch_id,
            "center": {"x": 10, "y": 10},
            "major_axis": 8,
            "minor_axis": 4,
            "rotation": 0.785398  # 45 degrees in radians
        }
        
        print(f"   Parameters: {ellipse_params_rotation}")
        
        request = {
            "method": "fusion.create_ellipse",
            "params": ellipse_params_rotation,
            "id": 4
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        ellipse_response_2 = json.loads(response)
        print("   Response:")
        print(json.dumps(ellipse_response_2, indent=2))
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_ellipse_response()
