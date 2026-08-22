import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.utils import degree
from neo4j_to_pyg import fetch_graph
from neo4j import GraphDatabase
from torch_geometric.data import Data

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")

class BaselineGCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        return self.conv2(x, edge_index)

def build_data():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        edges = session.execute_read(fetch_graph)
    driver.close()

    node_ids = sorted({n for src, dst, _ in edges for n in (src, dst)})
    id_to_idx = {node_id: i for i, node_id in enumerate(node_ids)}
    src_idx = [id_to_idx[s] for s, d, _ in edges]
    dst_idx = [id_to_idx[d] for s, d, _ in edges]
    edge_index = torch.tensor([src_idx, dst_idx], dtype=torch.long)

    x = torch.ones((len(node_ids), 2), dtype=torch.float)
    deg = degree(edge_index[0], num_nodes=len(node_ids))
    y = (deg > deg.median()).long()  # dummy label: "high degree" or not

    return Data(x=x, edge_index=edge_index, y=y)

if __name__ == "__main__":
    data = build_data()
    model = BaselineGCN(in_channels=2, hidden_channels=8, out_channels=2)
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

    print(f"\nFinal accuracy on dummy 'high-degree' label: {acc:.2%}")
    print("This confirms the real graph -> GCN training loop works end to end.")
