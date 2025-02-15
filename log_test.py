import os
import json
import cv2
import time
import base64
import numpy as np

def display_images_and_log_actions(log_folder):
    log_dir = os.path.join(os.getcwd(), log_folder)

    # Check if the log directory exists
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"The directory {log_dir} does not exist.")
    
    # Get the list of state JSON files in the log directory,
    # sorted based on the number in the file name (i.e., state_[number].json)
    state_list = sorted(os.listdir(log_dir), key=lambda x: int(x.split('_')[1].split('.')[0]))
    for state_json in state_list:
        with open(os.path.join(log_dir, state_json), 'r') as file:
            state = json.load(file)
        
        # Decode the base64 image
        image_data = base64.b64decode(state['image'])
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Display the image
        cv2.imshow('User Action', image)
        cv2.waitKey(0)  # Display each image for 1 second
        cv2.destroyAllWindows()
        
        # Print the action log
        print(f"Timestamp: {state['timestamp']}")
        print(f"Action Type: {state['action_type']}")
        print(f"Action Log: {state['action_log']}")
        print("-" * 50)

        if state['action_type'] == 'mouse_click' or state['action_type'] == 'mouse_drag':
            # Decode the base64 image
            image_data = base64.b64decode(state['action_image'])
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            # Display the image
            cv2.imshow('Mouse Click Patch', image)
            cv2.waitKey(0)
    

if __name__ == "__main__":
    log_folder = input("Enter the name of the log folder: ")
    display_images_and_log_actions(log_folder)