def user_input_prompt(action_type, action_log):
    if action_type == 'typing':
        return f"The user typed {action_log}"
    elif action_type == 'mouse_click':
        return f"The user pressed the {action_log['input']} button at the coordinates, {action_log['coordinates']}. You are also supplied with an image containing a patch of the screen centered at these coordinates."
    elif action_type == "mouse_scroll":
        return f"The user scrolled {action_log['delta']} pixels in the x and y directions"
    elif action_type == "shortcut":
        return f"The user executed the shortcut {'+'.join(action_log)}"
    elif action_type == "mouse_drag":
        return f"The user dragged the mouse from the coordinates {action_log['initial']} to {action_log['final']}. You are also supplied with an image illustrating this action."
    elif action_type == "special_key":
        return f"The user pressed the {action_log} key."
    else:
        raise ValueError("invalid action type")

def system_prompt(mode):
    if mode == "user_input":
        return "You are an AI assistant that will describe the computer actions of a human user as a simple step. You will be supplied with a snapshot of the user's screen before and after the action, as well as information about the action itself. Answer concisely and accurately, ideally in thirteen words or less."
    elif mode == "summarise_inputs":
        return "You will be supplied with a set of tasks performed by the user, you must output a succinct summary of the tasks performed."
    elif mode == "generate_new_actions":
        return "You will be supplied with a summary of the user's actions and a user change. You must generate a new set of actions based on the user change. Each action should perform one particular goal, and ideally only take one user operation to accomplish. Avoid generating redundant actions. Actions should be described in a concise and clear manner as imperative commands. Separate each action with a newline character."
    elif mode == "determine_inputs":
        return "You are an AI assistant that will determine the next computer input needed to perform a specific task. You will be supplied with a description of the task and the current state of the computer. You must output the computer input needed to perform the task. The input should be described in a clear and concise manner, 'e.g. Click the Start button' or 'Type 'Hello', do not do json format, asnwer in plain text"
    elif mode == "check_complete":
        return "You are an AI assistant that will determine if a task has been completed. You will be supplied with a description of the task, the initial state of the computer, the current state of the computer, and the inputs that have been performed to complete the task. You must output whether the task has been completed or not. The task is considered completed if the computer state matches the desired state. Just output True or False"