import pandas as pd
import os

# Paths
CSV_FILE = "./data/puzzles.csv"
OUTPUT_FILE = "./data/coach_training_set.csv"

def extract_lessons(target_themes=['fork', 'pin', 'hangingPiece'], puzzles_per_theme=5000):
    print(f"📖 Reading master database...")
    # Read in chunks to save RAM
    chunks = pd.read_csv(CSV_FILE, chunksize=100000)
    
    collected_puzzles = []
    counts = {theme: 0 for theme in target_themes}

    for chunk in chunks:
        for theme in target_themes:
            if counts[theme] < puzzles_per_theme:
                # Find puzzles containing this specific theme
                match = chunk[chunk['Themes'].str.contains(theme, case=False, na=False)]
                
                # Take only what we need to hit the limit
                needed = puzzles_per_theme - counts[theme]
                to_add = match.head(needed)
                
                collected_puzzles.append(to_add)
                counts[theme] += len(to_add)
        
        # Stop early if we have enough of everything
        if all(c >= puzzles_per_theme for c in counts.values()):
            break

    # Combine and save
    final_df = pd.concat(collected_puzzles).drop_duplicates(subset=['PuzzleId'])
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Extraction Complete! Saved {len(final_df)} puzzles to {OUTPUT_FILE}")
    print(f"Stats: {counts}")

if __name__ == "__main__":
    extract_lessons()