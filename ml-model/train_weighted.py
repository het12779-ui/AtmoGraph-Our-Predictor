import torch
import torch.nn.functional as F
from train_gat_baseline import BaselineGAT
from build_real_data import build_real_data

data = build_real_data()

counts = torch.bincount(data.y, minlength=3).float()
print("Label counts (low, medium, high):", counts.tolist())

# Inverse-frequency weighting: rare classes get a bigger penalty when missed
weights = counts.sum() / (counts.clamp(min=1) * len(counts))
print("Class weights:", weights.tolist())

model = BaselineGAT(in_channels=2, hidden_channels=8, out_channels=3)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

model.train()
for epoch in range(1, 51):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = F.cross_entropy(out, data.y, weight=weights)
    loss.backward()
    optimizer.step()
    if epoch % 10 == 0 or epoch == 1:
        print(f"Epoch {epoch:3d} | Weighted loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    pred = model(data.x, data.edge_index).argmax(dim=1)
    labels = ["low", "medium", "high"]
    for i, name in enumerate(labels):
        mask = data.y == i
        if mask.sum() > 0:
            class_acc = (pred[mask] == data.y[mask]).float().mean().item()
            print(f"  {name}: {int(mask.sum())} nodes, accuracy {class_acc:.2%}")
