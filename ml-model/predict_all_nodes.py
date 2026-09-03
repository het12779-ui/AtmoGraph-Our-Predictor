import json
import torch
from train_gat_baseline import BaselineGAT
from build_real_data import build_real_data
from neo4j_to_pyg import fetch_graph
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
LABELS = ["low", "medium", "high"]

data = build_real_data()

model = BaselineGAT(in_channels=2, hidden_channels=8, out_channels=3)
model.load_state_dict(torch.load("weighted_gat_week2.pt"))
model.eval()

driver = GraphDatabase.driver(URI, auth=AUTH)
with driver.session() as session:
    edges = session.execute_read(fetch_graph)
driver.close()

node_ids = sorted({n for src, dst, _ in edges for n in (src, dst)})

with torch.no_grad():
    preds = model(data.x, data.edge_index).argmax(dim=1)

results = []
disagreements = 0

for idx, node_id in enumerate(node_ids):
    predicted = LABELS[preds[idx].item()]
    actual = LABELS[data.y[idx].item()]
    if predicted != actual:
        disagreements += 1
    results.append({
        "node_id": node_id,
        "predicted_risk": predicted,
        "actual_risk": actual
    })

with open("predicted_risks.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Predicted risk for {len(results)} nodes.")
print(f"Model disagreed with the news-driven actual risk on {disagreements} node(s).")
print("Saved predicted_risks.json -- worth reviewing the disagreements together as a team.")
