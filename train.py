# Phase 6: The Training Loop (The Learning Phase)
# This is where all your hard work comes together. We will now take the Brain (Model), the Textbook (Dataset), and a Loss Function (the "Judge") to start the training process.

# 1. Create the Training Script
# Create a new file named train.py. This script will run through your 14,740 puzzles and teach the AI to recognize the themes.

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from dataset import ChessCoachDataset
from model import ChessCoachAI

# 1. SETUP HARDWARE & DATA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load 8 puzzles at a time (Batch Size)
dataset = ChessCoachDataset("./data/coach_training_set.csv")
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# 2. INITIALIZE MODEL, LOSS, AND OPTIMIZER
model = ChessCoachAI().to(device)
criterion = nn.CrossEntropyLoss() # The "Judge" - measures how wrong the AI is
optimizer = optim.Adam(model.parameters(), lr=0.001) # The "Optimizer" - fixes the Brain

# 3. THE TRAINING LOOP
def train(epochs=5):
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)

            # Zero the gradients
            optimizer.zero_grad()

            # Forward pass: Make a guess
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            # Backward pass: Learn from mistakes
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            
            if i % 100 == 99:    # Print every 100 batches
                print(f'[Epoch {epoch + 1}, Batch {i + 1}] Loss: {running_loss / 100:.3f}')
                running_loss = 0.0

    print("✅ Training Complete!")
    # Save the "Brain" for later use
    torch.save(model.state_dict(), "chess_coach_model.pth")
    print("💾 Model saved as 'chess_coach_model.pth'")

if __name__ == "__main__":
    train(epochs=5)