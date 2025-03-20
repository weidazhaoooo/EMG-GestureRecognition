import zmq
import time
import sys

class EMGPublisher:
    def __init__(self, ip="tcp://127.0.0.1:5000"):
        """Initialize ZMQ publisher for EMG classification results"""
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(ip)
        print(f"ZMQ Publisher initialized at {ip}")
        # Allow time for connection to establish
        time.sleep(0.5)
    
    def publish_result(self, gesture_class):
        """Publish gesture classification result to Unity"""
        try:
            # Convert the classification result to string
            message = str(gesture_class)
            self.socket.send_string(message)
            print(f"Published: {message}")
            return True
        except Exception as e:
            print(f"Error publishing message: {e}")
            return False
    
    def close(self):
        """Close the ZMQ connection"""
        self.socket.close()
        self.context.term()
        print("ZMQ publisher closed")