from functions import *
import time
import prompts

class Agent:

    def __init__(self,client,deployment):
        self.client = client
        self.deployment = deployment
    
    def query(self,messages):
        complete = False
        while not complete:
            # try:
            completion = self.client.chat.completions.create(  
                model=self.deployment,  
                messages=messages,  
                max_tokens=200,  
                temperature=0.7,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,  
                stop=None,  
                stream=False
            )
            complete = True
            # except:
            #     # wait for ten seconds
            #     print("Waiting for quota...\n")
            #     time.sleep(10)
        return completion.choices[0].message.content

    def process_user_actions(self,log_id,image_detail):

        action_list = []

        system_message = {
            "role": "system",
            "content": prompts.system_prompt("user_input")
        }

        user_actions = get_user_actions(log_id)

        for action in user_actions:

            user_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Initial user state:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": action.initial_state_image_url(),"detail": image_detail},
                        },
                        {
                            "type": "text",
                            "text": "Final user state:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": action.final_state_image_url(),"detail": image_detail},
                        },
                        {
                            "type": "text",
                            "text": action.description,
                        },
                    ]
                }
            
            if action.contains_image:
                user_message["content"].append({
                            "type": "image_url",
                            "image_url": {"url": action.action_image_url(), "detail": image_detail},
                        })
            
            

            messages = [system_message, user_message]
            
            # Generate the completion
            completion = self.query(messages)
            action_list.append(completion)
            
        return action_list

    def summarise_user_actions(self,action_list):
        
        system_message = {
            "role": "system",
            "content": prompts.system_prompt("summarise_inputs")
        }

        user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": action_list,
                    },
                ]
            }
        

        messages = [system_message, user_message]
        
        # Generate the completion
        summary = self.query(messages)
        return summary


    def generate_new_actions(self,task_summary,action_list,user_change):

        system_message = {
            "role": "system",
            "content": prompts.system_prompt("generate_new_actions")
        }

        user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Task summary: " + task_summary,
                    },
                    {
                        "type": "text",
                        "text": "Action list: " + action_list,
                    },
                    {
                        "type": "text",
                        "text": "User change: " + user_change,
                    },

                ]
            }

        messages = [system_message, user_message]
        
        # Generate the completion
        new_actions = self.query(messages).split("\n")
        return new_actions
    
    def determine_input(self,task_description,current_state):
        
        system_message = {
            "role": "system",
            "content": prompts.system_prompt("determine_inputs")
        }

        user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Task description: " + task_description,
                    },
                    {
                            "type": "image_url",
                            "image_url": {"url": current_state,"detail": "high"},
                    }
                ]
            }

        messages = [system_message, user_message]
        
        # Generate the completion
        actions = self.query(messages)
        return actions

    def check_complete(self,action,intial_state,current_state):

        system_message = {
            "role": "system",
            "content": prompts.system_prompt("check_complete")
        }

        user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Task description: " + action,
                    },
                    {
                        "type": "text",
                        "text": "Initial state: ",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": intial_state,"detail": "high"},
                    },
                    {
                        "type": "text",
                        "text": "Current state: ",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": current_state,"detail": "high"},
                    }
                ]
            }

        messages = [system_message, user_message]
        
        # Generate the completion
        complete = self.query(messages)
        complete = True if complete == "True" else False
        return complete