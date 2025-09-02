#!/usr/bin/env python3
"""
Test the direct sketch API to isolate the crash issue
"""
import socket
import json
import time

def test_direct_api():
    """Test the direct sketch creation"""
    try:
        # Connect to Fusion
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15.0)
        sock.connect(('localhost', 8765))
        print("✅ Connected to Fusion")
        
        # Send test request
        request = {
            "method": "fusion.test_direct_sketch",
            "params": {},
            "id": int(time.time() * 1000)
        }
        
        print("📤 Sending direct test request...")
        sock.send(json.dumps(request).encode('utf-8'))
        
        # Wait for response
        response_data = sock.recv(4096)
        if response_data:
            response = json.loads(response_data.decode('utf-8'))
            print(f"📥 Response: {response}")
        else:
            print("❌ No response received")
            
        sock.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Direct API Test")
    print("This bypasses MCP flow to test sketch creation directly")
    print()
    test_direct_api()





