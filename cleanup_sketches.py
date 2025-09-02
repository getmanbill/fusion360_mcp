#!/usr/bin/env python3
"""
Cleanup Sketches
Deletes problematic sketches before running complex test
"""

import socket
import json
import time

class FusionClient:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to Fusion")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 Disconnected")
    
    def send_request(self, method: str, params: dict = None) -> dict:
        if not self.socket:
            return None
        
        request = {
            "method": method,
            "params": params or {},
            "id": int(time.time() * 1000)
        }
        
        try:
            request_json = json.dumps(request)
            self.socket.send(request_json.encode('utf-8'))
            response_data = self.socket.recv(4096)
            
            if not response_data:
                return None
                
            response = json.loads(response_data.decode('utf-8'))
            time.sleep(1.0)  # Small delay between requests
            return response
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

def main():
    print("🧹 Cleaning up problematic sketches...")
    
    client = FusionClient()
    if not client.connect():
        return
    
    try:
        # List current sketches
        response = client.send_request("fusion.list_sketches")
        if response and response.get('result', {}).get('sketches'):
            sketches = response['result']['sketches']
            print(f"📝 Found {len(sketches)} sketches:")
            for sketch in sketches:
                print(f"   - {sketch['name']} (ID: {sketch['id'][:8]}...)")
            
            # Delete BracketProfile sketches
            sketches_to_delete = [s for s in sketches if s['name'].startswith('BracketProfile')]
            
            for sketch in sketches_to_delete:
                print(f"🗑️  Deleting {sketch['name']}...")
                del_response = client.send_request("fusion.delete_sketch", {"sketch_id": sketch['id']})
                
                if del_response and del_response.get('result', {}).get('success'):
                    print(f"✅ Deleted {sketch['name']}")
                else:
                    print(f"⚠️  Failed to delete {sketch['name']}")
        
        print("\n✅ Sketch cleanup complete!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Cleanup interrupted")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
