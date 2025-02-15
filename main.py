from openai import AzureOpenAI 
from agent import Agent
import os
from functions import get_screenshot
import time

endpoint = "https://aui-openai-api2.openai.azure.com/"
deployment = "gpt-4o"  
subscription_key = os.getenv("OPENAI_API_KEY")
image_detail = "low"

# Initialize Azure OpenAI client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",  
)

agent = Agent(client,deployment)

log_id = 'run_2025-02-15_16-05-45'

user_actions = "\n".join(agent.process_user_actions(log_id,image_detail))

task_summary = agent.summarise_user_actions(user_actions)

new_query = input("Enter the user new query: ")

new_actions = agent.generate_new_actions(task_summary,user_actions,new_query)

for action in new_actions:
    action_completed = False

    time.sleep(5)
    initial_state = get_screenshot()

    while not action_completed:
        agent_input = agent.determine_input(action,initial_state)
        #agent_input.execute()
        print(agent_input)
        time.sleep(5)
        current_state = get_screenshot()
        action_completed = agent.check_complete(action,initial_state,current_state)


