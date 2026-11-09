import os
import sys

EXPERIMENTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments")
if EXPERIMENTS not in sys.path:
    sys.path.insert(0, EXPERIMENTS)
