# Phase 5: The AI Brain (CNN Architecture)
# We are now going to build a Convolutional Neural Network (CNN). CNNs are famous for image recognition, but they are also incredibly powerful for chess because they scan the board for spatial patterns—like how three pieces are aligned during a Pin.

# 1. Create the Model Script
# Create a new file named model.py. This defines the actual "thinking" structure of your Chess Coach.

import torch
import torch.nn as nn
import torch.nn.functional as F

class ChessCoachAI(nn.Module):
    def __init__(self, num_themes=3):
        super(ChessCoachAI, self).__init__()
        
        # 1. First Layer: Scans 3x3 areas for basic piece relationships
        self.conv1 = nn.Conv2d(14, 64, kernel_size=3, padding=1)
        
        # 2. Second Layer: Looks for more complex tactical shapes
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        # 3. Third Layer: Deep features
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        
        # 4. Final "Decision" Layers (Fully Connected)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, num_themes) # Outputs 3 scores (Fork, Pin, Hanging)

    def forward(self, x):
        # Pass through convolutions with ReLU activation
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        # Flatten the board into a single long vector
        x = x.view(-1, 128 * 8 * 8)
        
        # Decision time
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x

# --- Quick Test ---
if __name__ == "__main__":
    model = ChessCoachAI()
    dummy_input = torch.randn(1, 14, 8, 8) # One fake chess board
    output = model(dummy_input)
    print(f"Model Output Shape: {output.shape}") # Should be [1, 3]
    print(f"Prediction Scores: {output.detach().numpy()}")

# 2. Why this Architecture?
# Convolutions: These layers are like "sliding windows." They help the AI recognize a Fork regardless of whether it’s happening in the middle of the board or in the corner.

# ReLU: This is an "activation function" that helps the AI learn complex, non-linear relationships (i.e., "If the Queen is here AND the King is there AND a Knight can jump here, THEN it's a Fork").

# Final Output: It gives three numbers. The highest number is the AI's "best guess" for what the tactic is.
