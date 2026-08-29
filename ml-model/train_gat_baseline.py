import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from train_baseline_gcn import build_data

class BaselineGAT(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, heads=2):
        super().__init__()
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads)
        self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1)

    def forward(self, x, edge_index):
        x = F.elu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        return self.conv2(x, edge_index)

if __name__ == "__main__":
    data = build_data()
    num_nodes = data.num_nodes
    perm = torch.randperm(num_nodes)
    split = int(num_nodes * 0.8)
    train_idx, test_idx = perm[:split], perm[split:]

    model = BaselineGAT(in_channels=2, hidden_channels=8, out_channels=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    model.train()
    for epoch in range(1, 51):
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = F.cross_entropy(out[train_idx], data.y[train_idx])
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d} | Train loss: {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        pred = model(data.x, data.edge_index).argmax(dim=1)
        acc = (pred[test_idx] == data.y[test_idx]).float().mean().item()
        print(f"\nGAT held-out test accuracy: {acc:.2%} (compare to Devam's GCN number)")
