OPEN_AI_API_KEY =  "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" #: fill in your openai api key here

DOC_PATH = "api.txt"  # api doc path

BASELINE_MESSAGES = [
    ############### Initial Prompts ############### 
    '''
    Here is a python api doc for a quadruped robot called Pupper that resembles a real dog. Each line starting with `def` is a n api function call, whose function is intuitive from its name and the comments a line above. Reply "OK" after reading it, no extra comments or explanations are needed.
    
    ''',
    '''
    For each following input, I'll give you a command to make pupper do something.
    Based on this doc, decompose the action into function calls, and output them in a python script.
    No extra comments or explanations are needed.
    Reply OK after reading this.
    ''',
    ############ Change with caution ##############

    ############ Add your prompt below ############
    '''
    make pupper walk in a circle
    '''
]
