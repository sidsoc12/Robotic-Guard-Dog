# Description: This script is used to generate scripts for the robot to follow
# For the lab, you don't need to change anything in this file
# TODO: Step 8 and 9. Use this file to tell ChatGPT to make scripts for you. 

from model_api import *
from constants import *
from utils import *

RUN_CODE = False  # Set to True to run the code in the script (if ready)

def main():
    print(f"\nStarting prompting ChatGPT to auto-program your pupper")
    print("Type 'Bye!' to end the conversation")
    print("--------------------------------------\n")
    conversation = []
    for i, message in enumerate(BASELINE_MESSAGES):
        if i == 0:
            with open(DOC_PATH, "r") as f:
                apis = f.read()
            message = message + apis            
        get_response(message, conversation)
        if i > 1:
            save_script(conversation[-1]["content"])
    while True:
        message = input("User: ")
        if message == "Bye!":
            break
        get_response(message, conversation)
        #save_conversation(conversation, filename = "robot_script_response.txt")
        save_script(conversation[-1]["content"], run_code=RUN_CODE)
        
if __name__ == "__main__":
    main()