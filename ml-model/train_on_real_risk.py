import torch
import torch.nn.functional as F
from train_gat_baseline import BaselineGAT
from build_real_data import build_real_data

data = build_real_data()
print("Label distribution:", torch.bincount(data.y).tolist(), "(low, medium, high)")

model = BaselineGAT(in_channels=2, hidden_channels=8, out_channels=3)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

model.train()
for epoch in range(1, 51):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = F.cross_entropy(out, data.y)
    loss.backward()
    optimizer.step()
    
    if epoch % 10 == 0 or epoch == 1:
        print(f"Epoch {epoch:3d} | Loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    pred = model(data.x, data.edge_index).argmax(dim=1)
    acc = (pred == data.y).float().mean().item()
    print(f"\nAccuracy on real risk labels: {acc:.2%}")
