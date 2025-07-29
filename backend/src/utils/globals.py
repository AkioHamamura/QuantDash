import os

# Get the absolute path to the backend directory
# __file__ = /Users/jakobildstad/Dev/QuantDash/backend/src/utils/globals.py
# We need to go up 2 levels: utils -> src -> backend
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BACKEND_DIR, "cache")