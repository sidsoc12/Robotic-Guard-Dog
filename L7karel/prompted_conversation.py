# Description: This file is the entry point for a prompted conversation with GPT-3.5

# TODO: Steps 5 and 6. Use prompted conversation to prompt the user
from model_api import *

A_FANTASTIC_ROLE = "A talking ice cream cone" # TODO: Step 6 Update prompt and role
PROMPT ='''
        Now imagine you are a talking ice cream cone. 
        You have to be as funny as possible and make the human laugh using jokes related to ice cream.
        Start by introducing yourself briefly.
        '''


def main():
    print(f"\nStarting conversation with {A_FANTASTIC_ROLE} (ChatGPT)")
    print("Type 'Bye!' to end the conversation")
    print("--------------------------------------\n")
    conversation = []
    get_response(PROMPT, conversation)
    print(f"{A_FANTASTIC_ROLE}: ", conversation[-1]["content"])
    while True:
        message = input("You: ")
        if message == "Bye!":
            break
        get_response(message, conversation)
        # save_conversation(conversation, filename = "prompted_conversation.txt")
        print(f"{A_FANTASTIC_ROLE}: ", conversation[-1]["content"])
        

if __name__=="__main__":
    main()