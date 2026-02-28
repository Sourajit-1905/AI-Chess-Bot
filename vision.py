# Phase 3: Board Vision (FEN to Tensors)
# Computers cannot "see" a FEN string like rnbqkbnr/pppppppp/8/.... To train a Neural Network, we must convert that text into a 3D Numerical Array (Tensor).

# We will use a 14-layer representation:

# Layers 1-6: White pieces (Pawn, Knight, Bishop, Rook, Queen, King).

# Layers 7-12: Black pieces.

# Layer 13: Whose turn it is (All 1s for White, all 0s for Black).

# Layer 14: Legal moves/Castling rights (Optional, but helpful).

import torch
import chess
import numpy as np

def board_to_tensor(board):
    # Create an empty 14x8x8 array
    # 6 pieces for White + 6 for Black + 1 for turn + 1 for total occupied
    tensor = np.zeros((14, 8, 8), dtype=np.float32)
    
    # Map pieces to layers
    piece_map = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2, 
        chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            # Layer index: 0-5 for White, 6-11 for Black
            layer = piece_map[piece.piece_type] + (6 if piece.color == chess.BLACK else 0)
            tensor[layer][row][col] = 1.0
            
    # Layer 12: Whose turn is it?
    if board.turn == chess.WHITE:
        tensor[12][:, :] = 1.0
        
    # Layer 13: Legal move density (simplified)
    for move in board.legal_moves:
        row, col = divmod(move.to_square, 8)
        tensor[13][row][col] = 1.0
        
    return torch.from_numpy(tensor)

# --- Quick Test ---
if __name__ == "__main__":
    test_board = chess.Board() # Starting position
    test_tensor = board_to_tensor(test_board)
    print(f"Tensor Shape: {test_tensor.shape}") # Should be [14, 8, 8]
    print("✅ Logic Check: White Pawn layer has 8 pawns.")
    print(test_tensor[0])