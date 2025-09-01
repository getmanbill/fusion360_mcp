"""
MCP Communication Server for Fusion 360
Handles socket communication and request routing
"""
import socket
import threading
import json
import traceback
from typing import Dict, Any, Optional, Callable
import adsk.core

class MCPServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.server_socket = None
        self.server_thread = None
        self.handlers = {}
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.custom_event = None
        self.event_handler = None
        self.pending_requests = {}
        self.request_counter = 0
        self._setup_custom_event()
        
    def register_handler(self, method: str, handler: Callable):
        """Register a method handler"""
        self.handlers[method] = handler
        
    def start(self):
        """Start the MCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            self.server_thread = threading.Thread(target=self._handle_connections, daemon=True)
            self.server_thread.start()
            
            # Give a moment for the thread to start
            import time
            time.sleep(0.1)
            
        except Exception as e:
            error_msg = f'Failed to start server: {str(e)}\n{traceback.format_exc()}'
            self.ui.messageBox(error_msg)
            raise
            
    def stop(self):
        """Stop the MCP server"""
        if self.server_socket:
            self.server_socket.close()
        if self.custom_event:
            self.custom_event.remove(self.event_handler)
            
    def _setup_custom_event(self):
        """Setup custom event for thread-safe API calls"""
        try:
            # Register custom event
            self.custom_event = self.app.registerCustomEvent('MCPAPICall')
            
            # Create event handler
            self.event_handler = MCPAPICallEventHandler(self)
            self.custom_event.add(self.event_handler)
            
        except Exception as e:
            self.ui.messageBox(f'Failed to setup custom event: {str(e)}')
            
    def _handle_connections(self):
        """Handle incoming connections"""
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket,), 
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                # Socket was closed
                break
                
    def _handle_client(self, client_socket):
        """Handle a single client connection"""
        try:
            import threading
            thread_id = threading.current_thread().ident
            # Log thread info (comment out to reduce message boxes)
            # self.ui.messageBox(f"🔗 [CLIENT] New client thread {thread_id} started", "Threading Debug")
            
            while True:
                data = client_socket.recv(4096)
                if not data:
                    # self.ui.messageBox(f"🔌 [CLIENT] Thread {thread_id} - client disconnected", "Threading Debug")
                    break
                    
                try:
                    request = json.loads(data.decode('utf-8'))
                    method = request.get('method', 'unknown')
                    # self.ui.messageBox(f"📥 [CLIENT] Thread {thread_id} - received {method}", "Threading Debug")
                    
                    response = self._process_request(request)
                    
                    # self.ui.messageBox(f"📤 [CLIENT] Thread {thread_id} - sending response for {method}", "Threading Debug")
                    response_json = json.dumps(response) + '\n'
                    client_socket.send(response_json.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.ui.messageBox(f"❌ [CLIENT] Thread {thread_id} - JSON decode error", "Threading Debug")
                    error_response = {
                        "error": "Invalid JSON",
                        "code": -32700
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                except Exception as e:
                    self.ui.messageBox(f"💥 [CLIENT] Thread {thread_id} - Exception: {str(e)}", "Threading Debug")
                    pass
                    
        except Exception as e:
            self.ui.messageBox(f"🚨 [CLIENT] Thread {thread_id} - Fatal error: {str(e)}", "Threading Debug")
            pass
        finally:
            self.ui.messageBox(f"🏁 [CLIENT] Thread {thread_id} - closing connection", "Threading Debug")
            client_socket.close()
            
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP request and return response"""
        try:
            import threading
            thread_id = threading.current_thread().ident
            
            method = request.get('method', '')
            params = request.get('params', {})
            request_id = request.get('id')
            
            # self.ui.messageBox(f"⚙️ [PROCESS] Thread {thread_id} - Processing {method}", "Threading Debug")
            
            # Find and call the handler
            if method in self.handlers:
                # CRITICAL FIX: Execute API calls on main thread to prevent crashes
                # This is the root cause of "connection forcibly closed" errors
                self.ui.messageBox(f"🎯 [PROCESS] Thread {thread_id} - Found handler for {method}", "Method Found")
                result = self._execute_on_main_thread(method, params)
                self.ui.messageBox(f"✅ [PROCESS] Thread {thread_id} - Main thread execution completed for {method}", "Execution Complete")
                
            else:
                available_methods = list(self.handlers.keys())
                self.ui.messageBox(f"❓ [PROCESS] Thread {thread_id} - Unknown method: {method}\nAvailable methods: {', '.join(available_methods[:5])}", "Unknown Method")
                return {
                    "error": f"Unknown method: {method}",
                    "code": -32601,
                    "id": request_id
                }
            
            # self.ui.messageBox(f"📋 [PROCESS] Thread {thread_id} - Returning result for {method}", "Threading Debug")
            return {
                "result": result,
                "id": request_id
            }
            
        except Exception as e:
            self.ui.messageBox(f"💥 [PROCESS] Thread {threading.current_thread().ident} - Exception: {str(e)}", "Threading Debug")
            return {
                "error": str(e),
                "code": -32603,
                "id": request.get('id')
            }
    
    def _execute_on_main_thread(self, method: str, params: Dict[str, Any]):
        """Execute handler on main UI thread using custom events"""
        try:
            import threading
            import time
            thread_id = threading.current_thread().ident
            main_thread_id = threading.main_thread().ident
            
            # self.ui.messageBox(f"🧵 [MAIN] Current thread: {thread_id}, Main thread: {main_thread_id}", "Threading Debug")
            
            if thread_id == main_thread_id:
                # Already on main thread, execute directly
                return self.handlers[method](params)
            else:
                # On background thread, use custom event
                # Debug message disabled to reduce noise
                # self.ui.messageBox(f"🔄 [THREAD] Marshaling {method} to main thread via custom event", "Threading Debug")
                
                # Create unique request ID
                request_id = self.request_counter
                self.request_counter += 1
                
                # Store request data
                self.pending_requests[request_id] = {
                    'method': method,
                    'params': params,
                    'result': None,
                    'error': None,
                    'completed': False
                }
                
                # Fire custom event with request ID
                args = {'request_id': str(request_id)}
                self.app.fireCustomEvent('MCPAPICall', json.dumps(args))
                
                # Wait for completion (with timeout)
                timeout = 30  # 30 seconds timeout
                start_time = time.time()
                while not self.pending_requests[request_id]['completed']:
                    if time.time() - start_time > timeout:
                        return {"error": "Main thread execution timeout"}
                    time.sleep(0.01)  # Small sleep to avoid busy waiting
                
                # Get result
                request_data = self.pending_requests.pop(request_id)
                if request_data['error']:
                    return {"error": request_data['error']}
                return request_data['result']
            
        except Exception as e:
            return {"error": f"Main thread execution failed: {str(e)}"}


class MCPAPICallEventHandler(adsk.core.CustomEventHandler):
    """Handler for custom events to execute API calls on main thread"""
    def __init__(self, server):
        super().__init__()
        self.server = server
        
    def notify(self, args):
        """Handle the custom event on main thread"""
        try:
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            
            # Parse the request ID from event data
            event_data = json.loads(eventArgs.additionalInfo)
            request_id = int(event_data['request_id'])
            
            # Get the pending request
            if request_id in self.server.pending_requests:
                request_data = self.server.pending_requests[request_id]
                method = request_data['method']
                params = request_data['params']
                
                try:
                    # Execute the handler on main thread with extra safety
                    # This is where Fusion API calls happen - must be bulletproof
                    result = self.server.handlers[method](params)
                    request_data['result'] = result
                except Exception as e:
                    # Catch ALL exceptions to prevent Fusion crashes
                    import traceback
                    error_detail = f"{str(e)}\n{traceback.format_exc()}"
                    request_data['error'] = str(e)
                    # Log detailed error for debugging
                    try:
                        self.server.ui.messageBox(f"Handler error in {method}: {error_detail}", "API Error")
                    except:
                        pass  # Even message box might fail during a crash
                    
                # Mark as completed
                request_data['completed'] = True
                
        except Exception as e:
            # Log error but don't crash
            self.server.ui.messageBox(f"Custom event error: {str(e)}")
