import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty("rate", 150)  # Speed of speech
engine.setProperty("volume", 0.9)  # Volume (0.0 to 1.0)

# Statements to speak
statements = [
    "Hello, I am your robotic dog.",
    "I am now crouching.",
    "Danger detected, stay back!",
    "All systems are operational.",
]

# Speak each statement
for statement in statements:
    engine.say(statement)
    engine.runAndWait()  # Blocks while processing all currently queued commands

engine.stop()
