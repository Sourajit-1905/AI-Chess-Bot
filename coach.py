import torch
import chess
import chess.engine
import os
import random
from vision import board_to_tensor
from model import ChessCoachAI
from phrases import CONFIRMATION_PHRASES

# --- CONFIGURATION ---
DEVICE = torch.device("cpu")
THEMES = ['is BEST', 'a Pin', 'a Hanging Piece']
STOCKFISH_PATH = r"C:\Users\Biswajit\Desktop\2nd Year\Exp\stockfish\stockfish-windows-x86-64-avx2.exe"
MODEL_PATH = "chess_coach_model.pth"

# 1. LOAD THE TRAINED BRAIN
def load_coach():
    model = ChessCoachAI(num_themes=3)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        print("🧠 AI Coach Brain loaded successfully.")
        return model
    else:
        raise FileNotFoundError("❌ Model file not found.")

# 2. ANALYSIS ENGINE (Optimized for Sub-1 Second Speed)
def ask_coach(fen, model, engine):
    board = chess.Board(fen)
    
    # A. AI Analysis (Theme detection)
    input_tensor = board_to_tensor(board).unsqueeze(0)
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        theme_idx = torch.argmax(probabilities).item()
        confidence = probabilities[0][theme_idx].item() * 100

    # B. Stockfish Analysis (Move detection)
    # Using 0.1s limit for speed; engine is already open
    result = engine.play(board, chess.engine.Limit(time=0.1))
    best_move = result.move

    # C. Threshold & Phrase Logic
    if confidence >= 85:
        explanation = f"I am VERY confident ({confidence:.1f}%) that the key theme here is {THEMES[theme_idx]}."
    else:
        # Replaces explanation with a random item from the list of 200
        explanation = random.choice(CONFIRMATION_PHRASES)

    # D. PREVIOUS FORMATTED OUTPUT
    print("\n" + "═"*45)
    print(" 🎓  AI CHESS COACH REPORT")
    print("═"*45)
    print(f" 📍  POSITION: {fen}")
    print(f" 🎯  BEST MOVE: {best_move}")
    print(f" 💡  INSIGHT: {explanation}")
    print("═"*45)
    print("👉 ACTION: Use the Recommended Move to capitalize on this tactic!")

if __name__ == "__main__":
    coach_model = load_coach()
    
    # START ENGINE ONCE (This is the secret to 1-second responses)
    print("🚀 Initializing Stockfish...")
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            print("✅ Engine Ready.")
            while True:
                user_fen = input("\nEnter FEN (or 'quit' to exit): ")
                if user_fen.lower() == 'quit':
                    break
                
                try:
                    ask_coach(user_fen, coach_model, engine)
                except ValueError:
                    print("❌ Invalid FEN. Please try again.")
    except Exception as e:
        print(f"❌ Error starting engine: {e}")