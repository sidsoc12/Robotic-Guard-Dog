# Description: Utility functions
# For the lab, you don't need to change anything in this file
import re, os

SCRIPT_FOLDER = "outputs"

def clean(txt):
    #print("Original:", txt)  # Uncomment this line to see the original text

    # if starts with word python
    if txt.startswith("python"):
        txt = txt[6:]

    # Sanitize the text
    # remove lines start "from pupper"
    txt = re.sub(r"from pupper.*?\n", "", txt)
    txt = re.sub(r"from Pupper.*?\n", "", txt)
    txt = re.sub(r"import .*?\n", "", txt)
 
    # remove all wakeup
    txt = re.sub(r"pupper.wakeup\(\)\n", "\n", txt)

    # add wakeup after pupper = Pupper()
    txt = re.sub(r"pupper = Pupper\(\)\n", "\n", txt)

    # add import statements
    txt = "import sys, time, math\nfrom StanfordQuadruped.karelPupper import *\npupper = Pupper()\npupper.wakeup()\n" + txt

    return txt

def save_script(txt, script_name = None, run_code = False):
    index = len(os.listdir(SCRIPT_FOLDER))
    if not script_name:
        script_name = f"script_{index}.py"
    else:
        script_name = script_name + ".py" if not script_name.endswith(".py") else script_name

    with open(os.path.join(SCRIPT_FOLDER, script_name), "w") as f:
        # capture parts within ''' '''
        parts = "\n".join(re.findall(r"```(.*?)```", txt, re.DOTALL))
        if not parts:
            parts = txt
        parts = clean(parts)
        #print("Cleaned:", parts)
        f.write(parts)
        f.write("\n")
        print(f"Saved script to {script_name}")

        try:
            if run_code:
                print("Running script...")
                exec(parts)
        except Exception as e:
            print("Error:", e)