import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import chess
import chess.engine
import torch
import random
import os
import sys
import subprocess

# --- CUSTOM MODULES ---
from vision import board_to_tensor
from model import ChessCoachAI
from phrases import CONFIRMATION_PHRASES
from voice import coach_voice 

# --- ICY GLASS PALETTE ---
COLOR_BASE = "#0B132B"      
COLOR_PANEL = "#1C2541"     
COLOR_ACCENT = "#5BC0BE"    
COLOR_TEXT = "#EDF2F4"      
COLOR_SUBTEXT = "#6FFFE9"   
COLOR_BTN_EXEC = "#3A506B"  
COLOR_BTN_RESET = "#5E60CE" 

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Correct paths for Deployment
STOCKFISH_PATH = resource_path(os.path.join("stockfish", "stockfish-windows-x86-64-avx2.exe"))
MODEL_PATH = resource_path("chess_coach_model.pth")
THEMES = ['is BEST', 'a Pin', 'a Hanging Piece']

class ChessCoachGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chess Coach")
        self.root.geometry("400x780")
        self.root.minsize(380, 650)
        self.root.maxsize(450, 850)
        self.root.attributes('-topmost', True) 
        self.root.configure(bg=COLOR_BASE)
        
        try:
            self.model = self.load_model()
            
            # --- HIDE CMD WINDOW FOR STOCKFISH ---
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.engine = chess.engine.SimpleEngine.popen_uci(
                STOCKFISH_PATH, 
                startupinfo=startupinfo
            )
        except Exception as e:
            messagebox.showerror("Startup Error", f"Initialization failed:\n{e}")
            root.destroy()

        self.setup_ui()

    def load_model(self):
        model = ChessCoachAI(num_themes=3)
        if os.path.exists(MODEL_PATH):
            model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
            model.eval()
            return model
        raise FileNotFoundError("AI Model file (.pth) not found.")

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg=COLOR_PANEL, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header = tk.Label(header_frame, text="AI COACH ANALYSIS", font=("Verdana", 14, "bold"), 
                          fg=COLOR_ACCENT, bg=COLOR_PANEL)
        header.pack(expand=True)

        main_content = tk.Frame(self.root, bg=COLOR_BASE, pady=20)
        main_content.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_content, text="INPUT FEN STRING", font=("Arial", 8, "bold"), 
                 bg=COLOR_BASE, fg=COLOR_SUBTEXT).pack(anchor="w", padx=40)
        
        self.fen_entry = tk.Entry(main_content, width=40, font=("Consolas", 10), 
                                  bg=COLOR_PANEL, fg=COLOR_TEXT, insertbackground=COLOR_ACCENT,
                                  bd=0, highlightthickness=1, highlightbackground=COLOR_ACCENT)
        self.fen_entry.pack(pady=10, padx=40, ipady=8)
        
        btn_frame = tk.Frame(main_content, bg=COLOR_BASE)
        btn_frame.pack(pady=15)

        self.btn_analyze = tk.Button(btn_frame, text="ANALYZE", command=self.start_analysis, 
                                     bg=COLOR_BTN_EXEC, fg=COLOR_TEXT, font=("Verdana", 8, "bold"), 
                                     width=16, height=2, relief="flat")
        self.btn_analyze.grid(row=0, column=0, padx=10)

        self.btn_clear = tk.Button(btn_frame, text="RESET", command=self.clear_log, 
                                   bg=COLOR_BTN_RESET, fg=COLOR_TEXT, font=("Verdana", 8, "bold"), 
                                   width=16, height=2, relief="flat")
        self.btn_clear.grid(row=0, column=1, padx=10)

        self.output_area = scrolledtext.ScrolledText(main_content, width=42, height=28, 
                                                     font=("Segoe UI Light", 11), bg=COLOR_PANEL, 
                                                     fg=COLOR_TEXT, bd=0, padx=25, pady=25)
        self.output_area.pack(pady=15, padx=40, fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)

    def log(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def clear_log(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete('1.0', tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.log("SYSTEM READY")

    def format_move(self, move):
        m = str(move)
        return f"{m[:2].upper()} to {m[2:].upper()}"

    def is_same_color_bishops_draw(self, board):
        pieces = board.piece_map()
        if len(pieces) == 4:
            bishops = [p for p in pieces.values() if p.piece_type == chess.BISHOP]
            if len(bishops) == 2:
                b_sq = [sq for sq, p in pieces.items() if p.piece_type == chess.BISHOP]
                return chess.square_dark(b_sq[0]) == chess.square_dark(b_sq[1])
        return False

    def start_analysis(self):
        fen = self.fen_entry.get().strip()
        
        # --- FEN VALIDATION ---
        if not fen:
            self.log("![ERROR] Input is empty.")
            return

        try:
            # Check if the FEN is a valid board configuration
            test_board = chess.Board(fen)
        except ValueError:
            self.log("~" * 30)
            self.log("![SYSTEM ERROR]")
            self.log("INVALID FEN DETECTED.")
            self.log("Please provide a valid board string.")
            self.log("~" * 30)
            messagebox.showwarning("Refraction Error", "The provided string is not a valid FEN code.")
            coach_voice.speak("Invalid FEN code detected.")
            return

        # Proceed if valid
        self.log("~" * 30)
        self.log("FEN Verified. Refracting Board State...")
        self.btn_analyze.config(state=tk.DISABLED)
        threading.Thread(target=self.run_logic, args=(fen,)).start()

    def run_logic(self, fen):
        try:
            board = chess.Board(fen)
            
            # 1. HARD TERMINAL STATES
            if board.is_checkmate():
                winner = "BLACK" if board.turn == chess.WHITE else "WHITE"
                msg = f"Checkmate. Victory for {winner}."
                self.root.after(0, lambda: self.show_results("GAME OVER", "None", msg))
                coach_voice.speak(msg)
                return

            if board.is_stalemate():
                msg = "Stalemate detected. The position is drawn."
                self.root.after(0, lambda: self.show_results("DRAW", "None", msg))
                coach_voice.speak(msg)
                return

            if board.is_insufficient_material() or self.is_same_color_bishops_draw(board):
                msg = "Draw by insufficient material."
                self.root.after(0, lambda: self.show_results("DRAW", "None", msg))
                coach_voice.speak(msg)
                return

            # 2. ENGINE & AI ANALYSIS
            input_tensor = board_to_tensor(board).unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(input_tensor)
                theme_idx = torch.argmax(torch.softmax(outputs, dim=1)).item()
                conf = torch.softmax(outputs, dim=1)[0][theme_idx].item() * 100

            info = self.engine.analyse(board, chess.engine.Limit(time=0.2))
            best_move_raw = info["pv"][0]
            best_move_text = self.format_move(best_move_raw)
            score = info["score"].relative

            # 3. EVAL-BASED DRAW LOGIC
            if score.is_mate():
                explanation = f"Critical. Forced mate in {abs(score.mate())} moves."
            elif score.score() == 0:
                explanation = "The position is technically drawn."
            elif conf >= 85:
                explanation = f"Analysis confirmed. Piece {THEMES[theme_idx]}."
            else:
                explanation = random.choice(CONFIRMATION_PHRASES)

            # 4. OUTPUT
            self.root.after(0, lambda: self.show_results(best_move_text, best_move_raw, explanation))
            coach_voice.speak(f"Best move is {best_move_text}. {explanation}")
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"ERROR: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.btn_analyze.config(state=tk.NORMAL))

    def show_results(self, move_display, move_raw, insight):
        if move_raw != "None":
            self.root.clipboard_clear()
            self.root.clipboard_append(str(move_raw))
            self.log(f"BEST MOVE: {move_display}")
        self.log(f"INSIGHT: {insight}")
        self.log("~" * 30)

    def on_closing(self):
        if hasattr(self, 'engine'): self.engine.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessCoachGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()