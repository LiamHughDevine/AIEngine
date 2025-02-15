import base64
from mimetypes import guess_type
import os
import json
import cv2
import prompts
import pyautogui
import numpy as np

# Define the UserAction class
class UserAction():
    def __init__(self, initial_state_image_b64, final_state_image_b64, action_log,action_type, contains_image, action_image_b64=None):
        self.initial_state_image_b64 = initial_state_image_b64
        self.final_state_image_b64 = final_state_image_b64
        self.action_type = action_type
        self.action_log = action_log
        self.contains_image = contains_image
        self.action_image_b64 = action_image_b64
        self.description = prompts.user_input_prompt(action_type,action_log)
    
    # convert the base64 image to a data url for parsing through the API
    def initial_state_image_url(self):
        return f"data:image/jpg;base64,{self.initial_state_image_b64}"
    def final_state_image_url(self):
        return f"data:image/jpg;base64,{self.final_state_image_b64}"
    def action_image_url(self):
        return f"data:image/jpg;base64,{self.action_image_b64}"


# Define a function to get user actions from a log directory
def get_user_actions(log_id):

    log_dir = os.path.join(os.getcwd(), 'logs', log_id)

    # Check if the log directory exists
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"The directory {log_dir} does not exist.")
    
    # Get the list of state JSON files in the log directory
    state_list = sorted(os.listdir(log_dir), key=lambda x: int(x.split('_')[1].split('.')[0]))
    user_actions = []

    # Extract user actions from the state JSON files and store them in a list for processing
    for n,state_json in enumerate(state_list):

        with open(os.path.join(log_dir, state_json), 'r') as file:
            state = json.load(file)
        
        # If this is not the first state, add the user action to the list
        if n != 0:
            final_state_image_b64 = state['image']
            if contains_image:
                user_actions.append(UserAction(initial_state_image_b64, final_state_image_b64, action_log, action_type, contains_image, action_image_b64))
            else:
                user_actions.append(UserAction(initial_state_image_b64, final_state_image_b64, action_log, action_type, contains_image))
        
        # Extract the relevant information from the state JSON for the next iteration
        initial_state_image_b64 = state['image']
        action_type = state['action_type']
        action_log = state['action_log']
        contains_image = (action_type in ['mouse_click','mouse_scroll'])
        if contains_image:
            action_image_b64 = state['action_image']


    return user_actions

def convert_to_base64(image):
    """Convert an image to a base64 encoded string."""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

# this function saves a b64 string to an image
def save_base64_to_image(base64_str, output_path):
    """Save a base64 encoded string to an image file."""
    image_data = base64.b64decode(base64_str)
    with open(output_path, 'wb') as file:
        file.write(image_data)

def get_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    base64_str = convert_to_base64(screenshot)
    return f"data:image/jpeg;base64,{base64_str}"