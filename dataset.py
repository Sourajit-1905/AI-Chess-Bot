# Phase 4: The Training Engine (PyTorch Dataset)
# Now we need to create the "Conveyor Belt." This code will take your filtered CSV file and feed those 14,740 puzzles into the AI one by one, converting each FEN into a tensor as it goes.

# 1. Create the Dataset Class
# Create a new file named dataset.py. This is the final structural piece before we build the actual AI model.

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import chess
from vision import board_to_tensor # Importing the logic you just tested

class ChessCoachDataset(Dataset):
    def __init__(self, csv_file):
        # Load our curated "lessons"
        self.df = pd.read_csv(csv_file)
        
        # Mapping our 3 themes to numbers (Labels)
        self.theme_to_idx = {'fork': 0, 'pin': 1, 'hangingPiece': 2}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # 1. Get the FEN and the primary Theme
        fen = self.df.iloc[idx]['FEN']
        themes_str = self.df.iloc[idx]['Themes'].lower()
        
        # 2. Determine the label (first match found)
        label = 0
        for theme, i in self.theme_to_idx.items():
            if theme in themes_str:
                label = i
                break
        
        # 3. Convert board to tensor
        board = chess.Board(fen)
        matrix = board_to_tensor(board)
        
        return matrix, torch.tensor(label, dtype=torch.long)

# --- Quick Test ---
if __name__ == "__main__":
    ds = ChessCoachDataset("./data/coach_training_set.csv")
    sample_board, sample_label = ds[0]
    
    print(f"Dataset loaded with {len(ds)} puzzles.")
    print(f"Input Shape: {sample_board.shape}") # Should be [14, 8, 8]
    print(f"Target Label (Theme Index): {sample_label.item()}")

# 2. Why this is the "Bridge"
# The Matrix: This is the Input (what the AI sees).

# The Label: This is the Answer Key (what the AI is trying to guess).

# The Result: By showing the AI thousands of these pairs, it starts to realize that whenever the "1s" in the Knight layer are in a specific pattern, the label is almost always "Fork."

