import os

# Define your message
message = "Hello, I am your robotic dog."

# Use the os.system method to call espeak with your message
os.system(f'espeak "{message}"')
