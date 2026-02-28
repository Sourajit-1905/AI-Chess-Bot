import os
import sys
import shutil
import torch
import chess.engine

# --- 1. CONFIGURATION ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- 2. HARDWARE DETECTION ---
def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda") # PC with NVIDIA GPU
    elif torch.backends.mps.is_available():
        return torch.device("mps")  # Mac M1/M2/M3
    return torch.device("cpu")      # Everything else

device = get_device()
print(f"AI Hardware: {device.type.upper()}")

# --- 3. TEACHER DETECTION (STOCKFISH) ---
def find_stockfish():
    # Check system path first
    path = shutil.which("stockfish")
    
    # Common manual paths if not in system PATH
    if not path:
        
        possible_paths = [
            # 1. Look for the exact file in your Exp folder
            r"C:\Users\Biswajit\Desktop\2nd Year\Exp\stockfish-windows-x86-64-avx2.exe",
            
            # 2. If it's inside that 'stockfish' folder I see in your sidebar:
            r"C:\Users\Biswajit\Desktop\2nd Year\Exp\stockfish\stockfish-windows-x86-64-avx2.exe",
            
            # 3. A simplified fallback if you rename the file
            r"C:\Users\Biswajit\Desktop\2nd Year\Exp\stockfish.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                path = p
                break
    
    if not path:
        print("❌ Stockfish not found! Please download it and update the path in this script.")
        return None
    
    # Test if it works
    try:
        with chess.engine.SimpleEngine.popen_uci(path) as engine:
            print(f"✅ Stockfish Teacher found at: {path}")
            return path
    except Exception as e:
        print(f"❌ Error starting Stockfish: {e}")
        return None

STOCKFISH_PATH = find_stockfish()

if __name__ == "__main__":
    print("--- Phase 1 Complete ---")
    print(f"Working Directory: {PROJECT_ROOT}")