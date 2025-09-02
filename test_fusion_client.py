#!/usr/bin/env python3
"""
Simple test client to communicate with Fusion 360 add-in
Run this script while the Fusion add-in is loaded to test basic functionality
"""

import socket
import json
import time
from typing import Dict, Any, Optional

class FusionClient:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self) -> bool:
        """Connect to the Fusion add-in"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # 10 second timeout
            self.socket.connect((self.host, self.port))
            print(f"[SUCCESS] Connected to Fusion add-in at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the Fusion add-in"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("[INFO] Disconnected from Fusion")
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a request to Fusion and get response"""
        if not self.socket:
            print("[ERROR] Not connected to Fusion")
            return None
        
        request = {
            "method": method,
            "params": params or {},
            "id": int(time.time() * 1000)  # Simple ID generation
        }
        
        try:
            # Send request
            request_json = json.dumps(request)
            print(f"[DEBUG] Sending request: {method}")
            self.socket.send(request_json.encode('utf-8'))
            
            # Receive response
            print(f"[DEBUG] Waiting for response (timeout in 10s)...")
            response_data = self.socket.recv(4096)
            print(f"[DEBUG] Received {len(response_data)} bytes")
            
            if not response_data:
                print("[ERROR] No response data received")
                return None
                
            response = json.loads(response_data.decode('utf-8'))
            print(f"[DEBUG] Parsed response successfully")
            
            return response
        except socket.timeout:
            print("[ERROR] Request timed out after 10 seconds")
            return None
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user (Ctrl+C)")
            raise
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None
    
    def get_document_info(self) -> Optional[Dict[str, Any]]:
        """Get basic document information"""
        return self.send_request("fusion.get_document_info")
    
    def list_parameters(self) -> Optional[Dict[str, Any]]:
        """List all user parameters"""
        return self.send_request("fusion.list_parameters")
    
    def set_parameter(self, name: str, value: float, units: str = "") -> Optional[Dict[str, Any]]:
        """Set a parameter value"""
        params = {
            "name": name,
            "value": value,
            "units": units
        }
        return self.send_request("fusion.set_parameter", params)

def print_response(title: str, response: Optional[Dict[str, Any]]):
    """Pretty print a response"""
    print(f"\n[INFO] {title}")
    print("-" * 50)
    if response:
        if "error" in response:
            print(f"[ERROR] {response['error']}")
        else:
            print(json.dumps(response.get('result', response), indent=2))
    else:
        print("[ERROR] No response received")

def main():
    """Main test function"""
    print("Fusion 360 Add-in Test Client")
    print("Make sure the Fusion add-in is loaded and running!")
    print()
    
    client = FusionClient()
    
    # Connect to Fusion
    if not client.connect():
        return
    
    try:
        # Test 1: Get document info
        response = client.get_document_info()
        print_response("Document Information", response)
        
        # Test 2: List parameters
        response = client.list_parameters()
        print_response("Current Parameters", response)
        
        # Test 3: Create/modify a parameter
        print("\n[TEST] Creating parameter...")
        response = client.set_parameter("TestParam", 42.0, "mm")
        print_response("Set Parameter Result", response)
        
        # Test 4: List parameters again to see the change
        response = client.list_parameters()
        print_response("Parameters After Modification", response)
        
        # Test 5: Modify existing parameter
        print("\n[TEST] Modifying parameter...")
        response = client.set_parameter("TestParam", 100.0, "mm")
        print_response("Modified Parameter Result", response)
        
    except KeyboardInterrupt:
        print("\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
