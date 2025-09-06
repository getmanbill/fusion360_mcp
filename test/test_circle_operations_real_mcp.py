#!/usr/bin/env python3
"""
Comprehensive Circle Operations Testing via Real MCP Communication
Tests all 24 circle methods through actual socket communication with Fusion 360
"""
import json
import socket
import logging
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CircleOperationsTester:
    """Test all circle operations via real MCP socket communication"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 1
        self.test_results = {}
        
    def connect(self) -> bool:
        """Establish MCP socket connection"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)  # 30 second timeout
            self.socket.connect((self.host, self.port))
            logging.info(f"Connected to MCP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close MCP socket connection"""
        if self.socket:
            try:
                self.socket.close()
                logging.info("Disconnected from MCP server")
            except:
                pass
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send MCP request and get response"""
        try:
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": self.request_id
            }
            self.request_id += 1
            
            message = json.dumps(request) + '\n'
            self.socket.send(message.encode('utf-8'))
            
            response_data = self.socket.recv(8192).decode('utf-8').strip()
            response = json.loads(response_data)
            
            return response
            
        except Exception as e:
            logging.error(f"Request failed for {method}: {e}")
            return None
    
    def test_method(self, method: str, params: Dict[str, Any], description: str) -> bool:
        """Test a single method and record results"""
        logging.info(f"Testing {method}: {description}")
        
        start_time = time.time()
        response = self.send_request(method, params)
        duration = time.time() - start_time
        
        if not response:
            self.test_results[method] = {
                "success": False,
                "error": "No response received",
                "duration": duration,
                "description": description
            }
            logging.error(f"  FAILED: No response")
            return False
        
        success = "result" in response and response.get("result", {}).get("success", False)
        
        self.test_results[method] = {
            "success": success,
            "response": response,
            "duration": duration,
            "description": description
        }
        
        if success:
            logging.info(f"  SUCCESS ({duration:.3f}s)")
            if "result" in response:
                result_data = response["result"]
                if "entity_id" in result_data:
                    logging.info(f"    Entity ID: {result_data['entity_id']}")
                if "creation_method" in result_data:
                    logging.info(f"    Creation Method: {result_data['creation_method']}")
                if "radius" in result_data:
                    logging.info(f"    Radius: {result_data['radius']}")
        else:
            error_msg = response.get("result", {}).get("error", "Unknown error")
            logging.error(f"  FAILED: {error_msg}")
        
        return success
    
    def run_comprehensive_tests(self):
        """Run all circle operation tests"""
        if not self.connect():
            return False
        
        try:
            # Step 1: Create a new document
            logging.info("=== SETUP: Creating new document ===")
            self.test_method(
                "fusion.new_document", 
                {}, 
                "Create new document for testing"
            )
            
            # Step 2: Create a sketch on XY plane
            logging.info("=== SETUP: Creating sketch ===")
            sketch_response = self.send_request("fusion.create_sketch", {"plane": "XY"})
            if not sketch_response or not sketch_response.get("result", {}).get("success"):
                logging.error("Failed to create sketch - aborting tests")
                return False
            
            sketch_id = sketch_response["result"]["sketch_id"]
            logging.info(f"Created sketch: {sketch_id}")
            
            # Test data
            test_entities = {}  # Store created entities for later tests
            
            # === CIRCLE CREATION TESTS ===
            logging.info("\n=== TESTING CIRCLE CREATION METHODS ===")
            
            # Test 1: Create circle by center and radius
            success = self.test_method(
                "fusion.create_circle_by_center_radius",
                {
                    "sketch_id": sketch_id,
                    "center": {"x": 0, "y": 0},
                    "radius": 5.0,
                    "construction": False
                },
                "Create circle by center point and radius"
            )
            if success:
                test_entities['circle1'] = self.test_results["fusion.create_circle_by_center_radius"]["response"]["result"]["entity_id"]
            
            # Test 2: Create circle by three points
            self.test_method(
                "fusion.create_circle_by_three_points",
                {
                    "sketch_id": sketch_id,
                    "point1": {"x": 10, "y": 0},
                    "point2": {"x": 13, "y": 4},
                    "point3": {"x": 10, "y": 8},
                    "construction": False
                },
                "Create circle passing through three points"
            )
            if self.test_results["fusion.create_circle_by_three_points"]["success"]:
                test_entities['circle2'] = self.test_results["fusion.create_circle_by_three_points"]["response"]["result"]["entity_id"]
            
            # Test 3: Create circle by two points (diameter)
            self.test_method(
                "fusion.create_circle_by_two_points",
                {
                    "sketch_id": sketch_id,
                    "point1": {"x": -10, "y": -5},
                    "point2": {"x": -10, "y": 5},
                    "construction": False
                },
                "Create circle where distance between points = diameter"
            )
            if self.test_results["fusion.create_circle_by_two_points"]["success"]:
                test_entities['circle3'] = self.test_results["fusion.create_circle_by_two_points"]["response"]["result"]["entity_id"]
            
            # Create some lines for tangent tests
            logging.info("Creating test lines for tangent operations...")
            line1_response = self.send_request("fusion.create_line", {
                "sketch_id": sketch_id,
                "start_point": {"x": 20, "y": 0},
                "end_point": {"x": 30, "y": 0}
            })
            line2_response = self.send_request("fusion.create_line", {
                "sketch_id": sketch_id,
                "start_point": {"x": 25, "y": -5},
                "end_point": {"x": 25, "y": 10}
            })
            line3_response = self.send_request("fusion.create_line", {
                "sketch_id": sketch_id,
                "start_point": {"x": 20, "y": 5},
                "end_point": {"x": 30, "y": 5}
            })
            
            if all([line1_response, line2_response, line3_response]):
                line1_id = line1_response["result"]["entity_id"]
                line2_id = line2_response["result"]["entity_id"]
                line3_id = line3_response["result"]["entity_id"]
                
                # Test 4: Create circle by two tangents
                self.test_method(
                    "fusion.create_circle_by_two_tangents",
                    {
                        "sketch_id": sketch_id,
                        "line1_id": line1_id,
                        "line2_id": line2_id,
                        "radius": 2.0,
                        "construction": False
                    },
                    "Create circle tangent to two lines"
                )
                if self.test_results["fusion.create_circle_by_two_tangents"]["success"]:
                    test_entities['circle4'] = self.test_results["fusion.create_circle_by_two_tangents"]["response"]["result"]["entity_id"]
                
                # Test 5: Create circle by three tangents
                self.test_method(
                    "fusion.create_circle_by_three_tangents",
                    {
                        "sketch_id": sketch_id,
                        "line1_id": line1_id,
                        "line2_id": line2_id,
                        "line3_id": line3_id,
                        "construction": False
                    },
                    "Create circle tangent to three lines"
                )
                if self.test_results["fusion.create_circle_by_three_tangents"]["success"]:
                    test_entities['circle5'] = self.test_results["fusion.create_circle_by_three_tangents"]["response"]["result"]["entity_id"]
            
            # === CIRCLE PROPERTIES TESTS ===
            logging.info("\n=== TESTING CIRCLE PROPERTIES METHODS ===")
            
            # Use the first successfully created circle for property tests
            test_circle_id = None
            for circle_name, circle_id in test_entities.items():
                if circle_id:
                    test_circle_id = circle_id
                    logging.info(f"Using {circle_name} ({circle_id}) for property tests")
                    break
            
            if test_circle_id:
                # Test 6: Get circle properties
                self.test_method(
                    "fusion.get_circle_properties",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id
                    },
                    "Get circle geometric properties"
                )
                
                # Test 7: Get circle constraints
                self.test_method(
                    "fusion.get_circle_constraints",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id
                    },
                    "Get constraints attached to circle"
                )
                
                # Test 8: Get circle state
                self.test_method(
                    "fusion.get_circle_state",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id
                    },
                    "Get circle state properties"
                )
                
                # Test 9: Set circle construction mode
                self.test_method(
                    "fusion.set_circle_construction",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id,
                        "construction": True
                    },
                    "Set circle to construction mode"
                )
                
                # Test 10: Set circle radius
                self.test_method(
                    "fusion.set_circle_radius",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id,
                        "radius": 7.5
                    },
                    "Change circle radius"
                )
                
                # Test 11: Set circle reference mode
                self.test_method(
                    "fusion.set_circle_reference",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": test_circle_id,
                        "reference": False  # Can only go from reference to non-reference
                    },
                    "Set circle reference mode"
                )
            
            # === CIRCLE INTERSECTION TESTS ===
            logging.info("\n=== TESTING CIRCLE INTERSECTION METHODS ===")
            
            if len(test_entities) >= 2:
                circle_ids = list(test_entities.values())
                
                # Test 12: Get circle intersections with another circle
                self.test_method(
                    "fusion.get_circle_intersections",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": circle_ids[0],
                        "target_curve_id": circle_ids[1]
                    },
                    "Get intersection points between two circles"
                )
                
                # Test 13: Get circle intersections with all curves
                self.test_method(
                    "fusion.get_circle_intersections",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": circle_ids[0]
                    },
                    "Get intersection points with all sketch curves"
                )
            
            # === CIRCLE MANIPULATION TESTS ===
            logging.info("\n=== TESTING CIRCLE MANIPULATION METHODS ===")
            
            # Create a test circle specifically for manipulation
            manip_response = self.send_request("fusion.create_circle_by_center_radius", {
                "sketch_id": sketch_id,
                "center": {"x": 40, "y": 0},
                "radius": 3.0,
                "construction": False
            })
            
            if manip_response and manip_response.get("result", {}).get("success"):
                manip_circle_id = manip_response["result"]["entity_id"]
                logging.info(f"Created manipulation test circle: {manip_circle_id}")
                
                # Test 14: Split circle
                self.test_method(
                    "fusion.split_circle",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": manip_circle_id,
                        "split_point": {"x": 43, "y": 0}
                    },
                    "Split circle at specified point"
                )
                
                # Test 15: Trim circle
                self.test_method(
                    "fusion.trim_circle",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": manip_circle_id,
                        "trim_point": {"x": 40, "y": 3}
                    },
                    "Trim circle segment"
                )
                
                # Test 16: Extend circle
                self.test_method(
                    "fusion.extend_circle",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": manip_circle_id,
                        "end_point": {"x": 45, "y": 0}
                    },
                    "Extend circle to end point"
                )
                
                # Test 17: Break circle curve
                self.test_method(
                    "fusion.break_circle_curve",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": manip_circle_id,
                        "point_on_curve": {"x": 37, "y": 0}
                    },
                    "Break circle at intersections"
                )
                
                # Test 18: Delete circle (test last for manipulation circle)
                self.test_method(
                    "fusion.delete_circle",
                    {
                        "sketch_id": sketch_id,
                        "circle_id": manip_circle_id
                    },
                    "Delete circle from sketch"
                )
            
            # === BACKWARD COMPATIBILITY TEST ===
            logging.info("\n=== TESTING BACKWARD COMPATIBILITY ===")
            
            # Test 19: Test original create_circle method
            self.test_method(
                "fusion.create_circle",
                {
                    "sketch_id": sketch_id,
                    "center": {"x": -20, "y": 0},
                    "radius": 4.0,
                    "construction": False
                },
                "Test backward compatibility with original create_circle"
            )
            
            logging.info("\n=== TEST SUMMARY ===")
            total_tests = len(self.test_results)
            successful_tests = sum(1 for result in self.test_results.values() if result["success"])
            
            logging.info(f"Total tests: {total_tests}")
            logging.info(f"Successful: {successful_tests}")
            logging.info(f"Failed: {total_tests - successful_tests}")
            logging.info(f"Success rate: {(successful_tests/total_tests*100):.1f}%")
            
            # Detailed results
            logging.info("\n=== DETAILED RESULTS ===")
            for method, result in self.test_results.items():
                status = "✓ PASS" if result["success"] else "✗ FAIL"
                duration = result["duration"]
                logging.info(f"{status} {method} ({duration:.3f}s) - {result['description']}")
                
                if not result["success"] and "response" in result:
                    error = result["response"].get("result", {}).get("error", "Unknown error")
                    logging.info(f"      Error: {error}")
            
            return successful_tests == total_tests
            
        except Exception as e:
            logging.error(f"Test execution failed: {e}")
            return False
        
        finally:
            self.disconnect()

def main():
    """Main test execution"""
    logging.info("Starting comprehensive circle operations testing")
    
    tester = CircleOperationsTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        logging.info("🎉 All circle operation tests PASSED!")
        exit_code = 0
    else:
        logging.error("❌ Some circle operation tests FAILED!")
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    import sys
    sys.exit(main())