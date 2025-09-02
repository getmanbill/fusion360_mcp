#!/usr/bin/env python3
"""
Cleanup Bad Parameters
Deletes the problematic red parameters from the complex sketch test
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
    print("🧹 Cleaning up bad parameters...")
    
    # Parameters that are showing as red/invalid
    bad_params = [
        "BracketWidth",
        "BracketHeight", 
        "MountHoleDia",
        "CenterHoleDia",
        "EdgeOffset"
    ]
    
    client = FusionClient()
    if not client.connect():
        return
    
    try:
        for param_name in bad_params:
            print(f"🗑️  Deleting {param_name}...")
            response = client.send_request("fusion.delete_parameter", {"name": param_name})
            
            if response and response.get('result', {}).get('success'):
                print(f"✅ Deleted {param_name}")
            else:
                print(f"⚠️  {param_name} not found or already deleted")
        
        print("\n✅ Cleanup complete! Bad parameters removed.")
        print("Now you can re-run the complex sketch test.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Cleanup interrupted")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
