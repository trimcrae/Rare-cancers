import os
import sys

# Make the modalities scripts importable as top-level modules (fpocket_lib, etc.).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
