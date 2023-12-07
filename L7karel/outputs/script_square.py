import sys, time, math
#from StanfordQuadruped.karelPupper import *
from StanfordQuadruped.karelPupper import Pupper
from StanfordQuadruped.karelPupper import BehaviorState

# Initialize Pupper
pupper = Pupper()

# Wake up the Pupper
pupper.wakeup()

# Move forward
pupper.forward_for_time(1.5, 0.5, behavior=BehaviorState.TROT)

# TODO: Step 7. Make Pupper walk in a square using Karel Pupper commands and your turn() function

# Rest the Pupper
pupper.rest()

