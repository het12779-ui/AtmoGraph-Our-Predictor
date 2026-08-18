import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

# Node order: 0=Port, 1=Supplier A, 2=Supplier B, 3=Manufacturer, 4=Retailer
# Features: [criticality_score (0-1), current_risk (0-1)]
x = torch.tensor([
    [0.9, 0.1], # Port
    [0.6, 0.0], # Supplier A
    [0.5, 0.0], # Supplier B
    [0.8, 0.0], # Manufacturer
    [0.4, 0.0], # Retailer
], dtype=torch.float)

# Edges (source -> target), PyG wants both directions listed separately if the graph
# should be treated as undirected for message passing
edge_index = torch.tensor([
    [0, 1, 2, 3], # Port->SupplierA, SupplierA->SupplierB(via port), SupplierB->Mfg, Mfg->Retailer
    [1, 2, 3, 4],
], dtype=torch.long)

data = Data(x=x, edge_index=edge_index)
print(data)
print("Number of nodes:", data.num_nodes, "| Number of edges:", data.num_edges)

# One forward pass through a single GCN layer, just to confirm shapes work end to end
conv = GCNConv(in_channels=2, out_channels=4)
out = conv(data.x, data.edge_index)

print("\nOutput shape after one GCNConv layer:", out.shape)
print("If this printed a [5, 4] tensor with no errors, your graph structure is valid PyG input.")
