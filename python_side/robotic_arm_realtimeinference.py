'''
Instructions:
0. Install pynput and XGboost e.g. pip install pynput xgboost
1. Run python dino_jump.py - This launches the training tool.
2. Click on the pygame window thats opened to make sure windows sends the keypresses to that process.
3. Relax the Myo arm, and with your other hand press 0 - This labels the incoming data as class 0
4. Make a fist with your hand and press 1, to label the fist as 1.
5. Try making a closed and open fist and watching the bars change.
6. Once you've gathered enough data, exit the pygame window. This saves the data in data/vals0.dat and vals1.dat
7. If you make a mistake and wrongly classify data, delete vals0 and vals1 and regather
8. If your happy it works, change TRAINING_MODE to False.
9. Goto https://trex-runner.com/ and rerun dino_jump.py with TRAINING_MODE set to false.
10. Click in the brower to start the game and tell windows to send keypresses there
11. Try making a fist and seeing if the dino jumps

If it doesn't work, feel free to let me know in the discord: 
https://discord.com/invite/mG58PVyk83

- PerlinWarp
'''

import pygame
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
from sympy import false
import zmq
import time

from Classifier import Live_Classifier, MyoClassifier, EMGHandler
from xgboost import XGBClassifier

TRAINING_MODE = True



# Mapping of pose numbers to gesture strings
pose_to_gesture = {
    0: "F",   # Fist
    1: "OH",  # Open Hand
    2: "L",   # Left
    3: "R",   # Right
    4: "DN",  # Down
    5: "RX"   # Rest
}

def send_command_zmq(pose):
    """Send pose command to Unity via ZMQ"""
    # Map the pose number to a gesture string
    if pose in pose_to_gesture:
        gesture = pose_to_gesture[pose]
    else:
        gesture = "RX"  # Default to rest
        
    # Send the gesture string via ZMQ
    socket.send_string(gesture)
    print(f"ZMQ: Sent gesture: {gesture}")
    return gesture

def pose_handler(pose):
    if pose == 0:
        # fist
        send_command_zmq(0)
        print("hand closed")
        
    elif pose == 1:
        # relax
        send_command_zmq(1)
        print("hand opened")
        
    elif pose == 2:
        # turn left
        send_command_zmq(2)
        print("wrist left")

    elif pose == 3:
        # turn right
        send_command_zmq(3)
        print("wrist right")

    elif pose == 4:
        # close ring and pinky, open thumb and index and middle
        send_command_zmq(4)
        print("thumb, index, middle opened, ring and pinky closed")


if __name__ == '__main__':
    keyboard = Controller()



	# Initialize ZMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5000")
    print("ZMQ Publisher initialized at tcp://127.0.0.1:5000")

    pygame.init()
    w, h = 800, 320
    scr = pygame.display.set_mode((w, h))
    font = pygame.font.Font(None, 30)

    # Make an ML Model to train and test with live
    # XGBoost Classifier Example
    model = XGBClassifier(eval_metric='logloss')
    clr = Live_Classifier(model, name="XG", color=(50,50,255))
    m = MyoClassifier(clr, mode=emg_mode.PREPROCESSED, hist_len=10)

    hnd = EMGHandler(m)
    m.add_emg_handler(hnd)
    
    try:
        m.connect()
    except Exception as e:
        print(f"Error connecting to Myo: {e}")
        print("Continuing with limited functionality...")

    m.add_raw_pose_handler(pose_handler)

    # Set Myo LED color to model color
    m.set_leds(m.cls.color, m.cls.color)
    # Set pygame window name
    pygame.display.set_caption(m.cls.name)

    # Add manual gesture control
    last_send_time = time.time()
    
    try:
        while True:
            # Process pygame events for manual testing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
                elif event.type == pygame.KEYDOWN:
                    # Manual pose sending via number keys
                    if pygame.K_0 <= event.key <= pygame.K_5:
                        pose_num = event.key - pygame.K_0  # Convert key to number 0-5
                        send_command_zmq(pose_num)
                        print(f"Manual pose: {pose_num}")
            
            # Run the Myo, get more data
            m.run()
            # Run the classifier GUI
            m.run_gui(hnd, scr, font, w, h)
            
            # Optional: Send periodic updates (every 0.5 seconds)
            current_time = time.time()
            if current_time - last_send_time > 0.5:
                # Get current prediction from classifier if available
                if hasattr(m.cls, 'curr_class') and m.cls.curr_class is not None:
                    send_command_zmq(m.cls.curr_class)
                last_send_time = current_time

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        # Clean up resources
        try:
            m.disconnect()
        except:
            pass
        
        # Close ZMQ connection
        socket.close()
        context.term()
        print("ZMQ connection closed")
        
        pygame.quit()