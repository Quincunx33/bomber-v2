import sys
import os

# Add the current directory to sys.path to allow importing from bomber_v2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bomber_v2.main import main_entry

if __name__ == "__main__":
    main_entry()
