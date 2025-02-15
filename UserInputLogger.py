import numpy as np
import mss
import os
import time
import threading
from datetime import datetime  # Import for timestamping the folder
from pynput import keyboard, mouse
import math
import json  # Import JSON module for saving buffer contents
from queue import PriorityQueue
from PIL import Image
from functions import convert_to_base64
from screeninfo import get_monitors
import cv2

# Create a new timestamped folder in the working directory
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_directory = os.path.join(os.getcwd(), 'logs', f"run_{timestamp}")
os.makedirs(save_directory, exist_ok=True)

# Automatically detect screen resolution (using the first monitor)
monitor = get_monitors()[0]  # Using the primary monitor

# Define the screen capture area (full screen using the detected resolution)
monitor_area = {
    "top": monitor.y,  # Use 'y' for the top position
    "left": monitor.x,  # Use 'x' for the left position
    "width": monitor.width,
    "height": monitor.height
}

start_time = time.time() # Start time for the program
keyboard_buffer = [] # Buffer to accumulate keystrokes
buffer_lock = threading.Lock()  # Lock to handle synchronization
captured_frames = [] # Store the captured frames and their timestamps
event_queue = PriorityQueue() # Priority queue for handling of events
stop_event = threading.Event() # Create an event to stop the listeners
currently_pressed_keys = set() # Set to keep track of currently pressed keys
initial_click_position = None # Variable to store the initial click position
save_count = 0 # Counter for naming the saved files

# Global variables for scroll accumulation
accumulated_scroll_delta = {"dx": 0, "dy": 0}
scroll_event_timestamp = None

def add_event_to_queue(timestamp, action_type, action_log):
    """Add an event to the queue with a timestamp."""
    event = {
        'timestamp': timestamp,
        'action_type': action_type,
        'action_log': action_log
    }
    # Use the timestamp as the priority
    event_queue.put((timestamp, event))

def process_event_queue():
    """Process events in the queue in order of their timestamps."""
    save_count = 0
    while not event_queue.empty():
        # Get the next event from the queue
        _, event = event_queue.get()

        # Extract details from the event
        timestamp = event['timestamp']
        action_type = event['action_type']
        action_log = event['action_log']

        # Get the corresponding frame from the captured frames
        closest_frame = min(
            captured_frames,
            key=lambda x: abs(x[1] - (start_time + timestamp))
        )

        # Resize the full frame to 512x512 using Pillow
        full_frame_pil = Image.fromarray(closest_frame[0])
        resized_frame_pil = full_frame_pil.resize((512, 512), Image.Resampling.LANCZOS)

        if action_type in set(["mouse_click","mouse_drag"]):
            cropped_frame = extract_cropped_image(closest_frame[0], action_log, action_type)

        # Prepare JSON data
        json_data = {
            'timestamp': timestamp,
            'action_type': action_type,
            'action_log': action_log,
            'image': convert_to_base64(np.array(resized_frame_pil)),
            'action_image': convert_to_base64(cropped_frame) if action_type == "mouse_click" or action_type == "mouse_drag" else None,
        }

        # Save the event to a JSON file
        json_filename = os.path.join(save_directory, f"state_{save_count}.json")
        with open(json_filename, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Saved action to {json_filename}")
        save_count += 1  # Increment the save count for the next file        save_count += 1


def flush_keyboard_buffer():
    """Flush the keyboard buffer to a .json file and log file."""
    global keyboard_buffer
    with buffer_lock:
        if keyboard_buffer:
            # Calculate time elapsed since program start
            elapsed_time = keyboard_buffer[0]

            # Save the log content to a .json file
            add_event_to_queue(elapsed_time, "typing", "".join(keyboard_buffer[1:]))

            # Clear the buffer after writing
            keyboard_buffer = []  # Clear the buffer

def flush_scroll_event():
    """Flush any accumulated scroll events to the queue."""
    global accumulated_scroll_delta, scroll_event_timestamp
    if accumulated_scroll_delta["dx"] != 0 or accumulated_scroll_delta["dy"] != 0:
        add_event_to_queue(
            scroll_event_timestamp,
            "mouse_scroll",
            {"delta": (accumulated_scroll_delta["dx"], accumulated_scroll_delta["dy"])}
        )
        # Reset accumulation variables
        accumulated_scroll_delta = {"dx": 0, "dy": 0}
        scroll_event_timestamp = None

# Keyboard event handlers
def on_press(key):
    elapsed_time = time.time() - start_time  # Calculate time elapsed since program start
    flush_scroll_event() # Flush any accumulated scroll events to the queue

    if key == keyboard.Key.esc:
        flush_keyboard_buffer()  # Flush any remaining keyboard input to the file
        add_event_to_queue(elapsed_time+0.01,"end","") # add slight time delay so queue isnt messed up
        stop_event.set()  # Signal the event to stop the program
        return False  # Return False to stop the keyboard listener

    # if multiple pressed keys check for shortcut
    if '\\x' in str(key):
        flush_keyboard_buffer()
        add_event_to_queue(elapsed_time, "shortcut", [str(k).replace('Key.','') for k in currently_pressed_keys]+[chr(ord(eval(str(key)))+64)])
        return  # Avoid logging individual key press

    """Callback for key press events."""
    # Add the pressed key to the set of currently pressed keys
    currently_pressed_keys.add(key)

    if len(currently_pressed_keys) > 1:
        for shortcut_key in [keyboard.Key.ctrl_l,keyboard.Key.ctrl_r,keyboard.Key.alt_l,keyboard.Key.ctrl,keyboard.Key.cmd,keyboard.Key.alt]:
            if (shortcut_key in currently_pressed_keys):
                flush_keyboard_buffer()
                add_event_to_queue(elapsed_time, "shortcut", [str(_).replace('Key.','') for _ in currently_pressed_keys])
                return  # Avoid logging individual key press

    # Log the key press into the buffer (only regular keys, no special keys)
    with buffer_lock:
        if hasattr(key, 'char') and key.char is not None:
            if len(keyboard_buffer) == 0:
                # Add the timestamp for the first key press
                keyboard_buffer.append(elapsed_time)
            keyboard_buffer.append(key.char)  # Append regular key
            return
        elif key in [keyboard.Key.space, keyboard.Key.tab]:
            # Special keys that are logged but not stored in the buffer
            special_key_map = {
                keyboard.Key.space: " ",
                keyboard.Key.tab: "\t"
            }
            keyboard_buffer.append(special_key_map.get(key))  # Add to buffer
            return

        elif key == keyboard.Key.backspace:
            if len(keyboard_buffer) > 0:
                keyboard_buffer.pop()  # Remove the last character in the buffer when backspace is pressed
            return

    if key not in [keyboard.Key.ctrl_l,keyboard.Key.ctrl_r,keyboard.Key.alt_l,keyboard.Key.ctrl,keyboard.Key.cmd,keyboard.Key.alt]:
        # Other special keys are logged but not added to the buffer
        flush_keyboard_buffer()
        add_event_to_queue(elapsed_time, "special_key", str(key).replace('Key.',''))
    return

def on_release(key):
    """Callback for key release events."""
    global stop_event
    try:
        currently_pressed_keys.remove(key)
    except KeyError:
        pass

# Mouse event handlers
def on_click(x, y, button, pressed):
    """Callback for mouse click events."""
    global initial_click_position
    global mouse_pressed_time
    if pressed:
        # Record the initial position when the mouse is pressed
        initial_click_position = (x, y)
        mouse_pressed_time = time.time() - start_time
        flush_keyboard_buffer()
        flush_scroll_event()
    else:
        # Calculate the distance between the initial click and the release position
        distance = math.sqrt((x - initial_click_position[0]) ** 2 + (y - initial_click_position[1]) ** 2)
        
        # If the distance is greater than 15 pixels, log the drag event
        if distance > 15:
            add_event_to_queue(mouse_pressed_time, "mouse_drag", {"coordinates": (initial_click_position[0], initial_click_position[1], x, y), "input": str(button)})
        else:
            add_event_to_queue(mouse_pressed_time, "mouse_click", {"coordinates": (x, y), "input": str(button)})
        # Reset the initial position after the release
        initial_click_position = None

def on_scroll(x, y, dx, dy):
    """Callback for mouse scroll events."""
    global accumulated_scroll_delta, scroll_event_timestamp
    timestamp = time.time() - start_time  # Calculate time elapsed since program start
    
    if scroll_event_timestamp is None:
        # Start a new scroll sequence
        scroll_event_timestamp = timestamp

    # Accumulate deltas
    accumulated_scroll_delta["dx"] += dx
    accumulated_scroll_delta["dy"] += dy

def capture_screen():
    """Function to capture the screen."""
    global captured_frames
    with mss.mss() as sct:
        print(f"Recording started. The frames will be saved to: {save_directory}")
        while not stop_event.is_set():  # Check if the stop event is set to stop capturing
            # Capture the screen
            screenshot = sct.grab(monitor_area)
            
            # Convert the captured screen to a numpy array (OpenCV format)
            frame = np.array(screenshot)
            
            # Get the current time (elapsed since start)
            frame_time = time.time()
            
            # Save the frame and its timestamp
            captured_frames.append((frame, frame_time))

def start_listeners():
    """Start the keylogger and mouse listener in separate threads."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as key_listener:
        with mouse.Listener(on_click=on_click, on_scroll=on_scroll) as mouse_listener:
            # Keep listening until stop_event is set
            key_listener.join()
            mouse_listener.join()

def extract_cropped_image(frame, action_log, action_type):
    """Extract a cropped image around the click or drag location."""
    border_size = 64 # Border size around the click location(s)

    # Remove the alpha channel if present
    if frame.shape[2] == 4:
        frame = frame[:, :, :3]

    # Pad the image with a black border
    padded_frame = np.zeros((frame.shape[0] + 2 * border_size, frame.shape[1] + 2 * border_size, 3), dtype=np.uint8)
    padded_frame[border_size:border_size + frame.shape[0], border_size:border_size + frame.shape[1]] = frame
    frame = padded_frame

    # Determine the cropping coordinates
    if action_type == "mouse_click":
        # Extract the click position from the action log
        click_x, click_y = action_log['coordinates']

        # Determine the bounding box for the click area with an additional border, accounting for the padding
        x1 = click_x
        y1 = click_y
        x2 = click_x + 2 * border_size
        y2 = click_y + 2 * border_size

    elif action_type == "mouse_drag":
        # Extract the start and end positions from the action log
        start_x, start_y, end_x, end_y = action_log['coordinates']

        # Determine the bounding box for the drag area with an additional border, accounting for the padding
        x1 = min(start_x, end_x)
        y1 = min(start_y, end_y)
        x2 = max(start_x, end_x) + 2 * border_size
        y2 = max(start_y, end_y) + 2 * border_size

    # Extract the cropped part from the frame
    cropped_image = frame[y1:y2, x1:x2]

    if action_type == "mouse_drag":
        # Draw an arrow on the cropped image to indicate the drag direction
        arrow_color = (0, 0, 255)  # Green color for the arrow
        arrow_thickness = 2  # Thickness of the arrow line
        arrow_tip_length = 0.2  # Tip length of the arrow

        # Calculate the start and end points relative to the cropped image
        start_point = (start_x - x1 + border_size, start_y - y1 + border_size)
        end_point = (end_x - x1 + border_size, end_y - y1 + border_size)

        # Draw the arrow on the cropped image using OpenCV
        cropped_image = cv2.arrowedLine(cropped_image, start_point, end_point, arrow_color, arrow_thickness, tipLength=arrow_tip_length)

    return cropped_image
    

def main():
    """Main function to start the listeners and screen capture."""
    global stop_event
    print("Keylogger and screen recorder are running. Press ESC to stop.")

    # Start the listeners in separate threads
    listener_thread = threading.Thread(target=start_listeners)
    listener_thread.daemon = True  # Ensure the thread will exit when the main program exits
    listener_thread.start()

    # Start the screen capture in a separate thread
    capture_thread = threading.Thread(target=capture_screen)
    capture_thread.daemon = True  # Ensure the thread will exit when the main program exits
    capture_thread.start()

    # Wait for the stop event to be set (i.e., ESC is pressed)
    stop_event.wait()  # Wait until ESC is pressed

    # Stop the listener threads and capture thread once ESC is pressed
    print("Recording stopped.")
    process_event_queue()

if __name__ == "__main__":
    main()
