"""
Quick debug test to see what the slot method is actually returning
"""
import socket
import json

def debug_slot_response():
    """Debug what create_slot is actually returning"""
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
        print("📄 Document creation response:")
        print(json.dumps(json.loads(response), indent=2))
        
        # Create sketch
        request = {
            "method": "fusion.create_sketch",
            "params": {"plane_reference": "XY", "name": "DebugSketch"},
            "id": 2
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sketch_response = json.loads(response)
        sketch_id = sketch_response.get('result', {}).get('sketch_id')
        print("\n📐 Sketch creation response:")
        print(json.dumps(sketch_response, indent=2))
        
        # Test slot creation
        slot_params = {
            "sketch_id": sketch_id,
            "start_point": {"x": 0, "y": 0},
            "end_point": {"x": 10, "y": 0},
            "width": 5
        }
        
        print(f"\n🔧 Testing slot with parameters:")
        print(f"   sketch_id: {sketch_id}")
        print(f"   start_point: {slot_params['start_point']}")
        print(f"   end_point: {slot_params['end_point']}")
        print(f"   width: {slot_params['width']}")
        print(f"   slot_length: {((slot_params['end_point']['x'] - slot_params['start_point']['x'])**2 + (slot_params['end_point']['y'] - slot_params['start_point']['y'])**2)**0.5}")
        print(f"   radius: {slot_params['width'] / 2}")
        
        request = {
            "method": "fusion.create_slot",
            "params": slot_params,
            "id": 3
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        slot_response = json.loads(response)
        print("\n🔧 Slot creation response:")
        print(json.dumps(slot_response, indent=2))
        
        # Test vertical slot
        print("\n🧪 Testing vertical slot:")
        slot_params_vertical = {
            "sketch_id": sketch_id,
            "start_point": {"x": 20, "y": 0},
            "end_point": {"x": 20, "y": 15},
            "width": 3
        }
        
        print(f"   Parameters: {slot_params_vertical}")
        
        request = {
            "method": "fusion.create_slot",
            "params": slot_params_vertical,
            "id": 4
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        slot_response_2 = json.loads(response)
        print("   Response:")
        print(json.dumps(slot_response_2, indent=2))
        
        # Test minimal slot
        print("\n🧪 Testing minimal slot:")
        slot_params_minimal = {
            "sketch_id": sketch_id,
            "start_point": {"x": 30, "y": 0},
            "end_point": {"x": 32, "y": 0},
            "width": 1
        }
        
        print(f"   Parameters: {slot_params_minimal}")
        
        request = {
            "method": "fusion.create_slot",
            "params": slot_params_minimal,
            "id": 5
        }
        sock.send((json.dumps(request) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        slot_response_3 = json.loads(response)
        print("   Response:")
        print(json.dumps(slot_response_3, indent=2))
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_slot_response()
