import torch, torch.nn.functional as F
from torch_geometric.datasets import KarateClub
from torch_geometric.nn import GCNConv

class TinyGCN(torch.nn.Module):
    def __init__(self, nf, hd, nc):
        super().__init__()
        self.conv1 = GCNConv(nf, hd)
        self.conv2 = GCNConv(hd, nc)
    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        return self.conv2(x, edge_index)

dataset = KarateClub()
data = dataset[0]
model = TinyGCN(dataset.num_node_features, 16, dataset.num_classes)
opt = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

model.train()
for epoch in range(1, 101):
    opt.zero_grad()
    out = model(data.x, data.edge_index)
    loss = F.cross_entropy(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    opt.step()
    if epoch % 20 == 0 or epoch == 1:
        print(f"Epoch {epoch:3d} | Loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    pred = model(data.x, data.edge_index).argmax(dim=1)
    correct = (pred[data.train_mask] == data.y[data.train_mask]).sum()
    acc = int(correct) / int(data.train_mask.sum())
    print(f"\nFinal training accuracy: {acc:.2%}")
