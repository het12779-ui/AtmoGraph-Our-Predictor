import torch
import torch.nn.functional as F
from train_baseline_gcn import BaselineGCN, build_data

def main():
    data = build_data()
    num_nodes = data.num_nodes
    perm = torch.randperm(num_nodes)
    split = int(num_nodes * 0.8)
    train_idx, test_idx = perm[:split], perm[split:]
    
    model = BaselineGCN(in_channels=2, hidden_channels=8, out_channels=2)
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
        test_acc = (pred[test_idx] == data.y[test_idx]).float().mean().item()
        print(f"\nHeld-out test accuracy: {test_acc:.2%}")
        
    torch.save(model.state_dict(), "baseline_gcn_week1.pt")
    print("Saved checkpoint to baseline_gcn_week1.pt")

if __name__ == "__main__":
    main()
