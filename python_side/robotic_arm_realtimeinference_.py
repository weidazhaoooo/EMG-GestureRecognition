from zmq_publisher import EMGPublisher
import pygame
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
from sympy import false
from Classifier import Live_Classifier, MyoClassifier, EMGHandler
from xgboost import XGBClassifier
import time

# Map Myo's built-in pose indices to your gesture labels
POSE_TO_GESTURE = {
    0: "F",    # Fist
    1: "OH",   # Open Hand
    2: "L",    # Left
    3: "R",    # Right
    4: "DN",   # Down
    5: "RX",   # Rest/Default (not a built-in pose, used as fallback)
}

# Current gesture to send to Unity
current_gesture = "RX"  # Default to rest

def pose_handler(pose):
    global current_gesture
    
    # Map the pose index to your gesture label
    if pose in POSE_TO_GESTURE:
        current_gesture = POSE_TO_GESTURE[pose]
        print(f"Detected gesture: {current_gesture}")
    else:
        current_gesture = "RX"  # Default to rest
        print(f"Unknown pose {pose}, using default")

if __name__ == '__main__':
    pygame.init()
    w, h = 800, 320
    scr = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Myo Gesture Recognition")

    # Initialize the Myo connection
    model = XGBClassifier(eval_metric='logloss')
    clr = Live_Classifier(model, name="XG", color=(50,50,255))
    m = MyoClassifier(clr, mode=emg_mode.PREPROCESSED, hist_len=10)
    
    # Register the pose handler
    m.add_raw_pose_handler(pose_handler)
    
    # Set LED color
    m.set_leds((0, 128, 255), (0, 128, 255))
    
    # Initialize the ZMQ publisher
    #zmq_publisher = EMGPublisher()
    print("ZMQ publisher initialized. Waiting for Unity to connect...")

    try:
        while True:
            # Process Myo data
            m.run()
            
            # Send the current gesture to Unity via ZMQ
            #zmq_publisher.publish_result(current_gesture)
            print(f"Sent gesture: {current_gesture}")
            
            # Small delay to avoid flooding the connection
            pygame.time.delay(50)
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        # Clean up
        #zmq_publisher.close()
        m.disconnect()
        pygame.quit()
        print("Cleanup complete")