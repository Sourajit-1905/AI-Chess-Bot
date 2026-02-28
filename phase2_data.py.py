#Now that the "Coach" has a teacher, we need to give it a textbook. 
# We are going to download the Lichess Puzzle Database (~3.5 million tactical positions) and filter it for specific themes
#  like "Forks" and "Pins."

import os
import requests
import zstandard as zstd
import shutil
import pandas as pd

# Set up paths relative to your project folder
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ZST_FILE = os.path.join(DATA_DIR, "puzzles.csv.zst")
CSV_FILE = os.path.join(DATA_DIR, "puzzles.csv")

def download_and_extract():
    url = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
    
    if not os.path.exists(CSV_FILE):
        print("⏳ Downloading 1GB Puzzle Database... (This depends on your internet speed)")
        with requests.get(url, stream=True) as r:
            with open(ZST_FILE, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        
        print("📦 Decompressing database into CSV...")
        with open(ZST_FILE, 'rb') as f_in:
            dctx = zstd.ZstdDecompressor()
            with open(CSV_FILE, 'wb') as f_out:
                dctx.copy_stream(f_in, f_out)
        print("✅ Raw Data Ready!")
    else:
        print("📚 Dataset already exists locally.")

def preview_data():
    # Read just the first 5 rows to make sure it's working
    df = pd.read_csv(CSV_FILE, nrows=5)
    print("\n--- Data Preview ---")
    print(df[['PuzzleId', 'FEN', 'Themes']])

if __name__ == "__main__":
    download_and_extract()
    preview_data()