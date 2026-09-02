import torch
from train_gat_baseline import BaselineGAT
from train_baseline_gcn import build_data

def explain_node(node_idx, x, edge_index, model, top_k=3):
    model.eval()
    with torch.no_grad():
        _, (edge_index_att, alpha) = model.conv1(
            x, edge_index, return_attention_weights=True
        )
    
    alpha = alpha.mean(dim=1)   # average across attention heads
    mask = edge_index_att[1] == node_idx
    src_nodes = edge_index_att[0][mask]
    scores = alpha[mask]
    
    k = min(top_k, len(scores))
    topk = torch.topk(scores, k)
    
    print(f"Top {k} contributing neighbors for node {node_idx}:")
    for score, i in zip(topk.values, topk.indices):
        neighbor = src_nodes[i].item()
        print(f"  neighbor node {neighbor}: attention weight = {score.item():.3f}")

if __name__ == "__main__":
    data = build_data()
    model = BaselineGAT(in_channels=2, hidden_channels=8, out_channels=2)
    # Today: freshly initialized weights, just to confirm attention extraction works
    # mechanically. Week 3 loads a real trained checkpoint here instead.
    explain_node(node_idx=0, x=data.x, edge_index=data.edge_index, model=model)
