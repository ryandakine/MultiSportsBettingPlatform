import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from src.api import routes
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
