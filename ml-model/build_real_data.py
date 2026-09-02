import torch
from torch_geometric.data import Data
from neo4j import GraphDatabase
from neo4j_to_pyg import fetch_graph

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
RISK_TO_LABEL = {"low": 0, "medium": 1, "high": 2}

def fetch_node_risks(tx):
    result = tx.run("MATCH (n) WHERE n.id IS NOT NULL RETURN n.id AS id, coalesce(n.risk, 'low') AS risk")
    return {r["id"]: r["risk"] for r in result}

def build_real_data():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        edges = session.execute_read(fetch_graph)
        risks = session.execute_read(fetch_node_risks)
    driver.close()
    
    node_ids = sorted({n for src, dst, _ in edges for n in (src, dst)})
    id_to_idx = {node_id: i for i, node_id in enumerate(node_ids)}
    
    src_idx = [id_to_idx[s] for s, d, _ in edges]
    dst_idx = [id_to_idx[d] for s, d, _ in edges]
    edge_index = torch.tensor([src_idx, dst_idx], dtype=torch.long)
    
    x = torch.ones((len(node_ids), 2), dtype=torch.float)
    y = torch.tensor(
        [RISK_TO_LABEL.get(risks.get(nid, "low"), 0) for nid in node_ids], dtype=torch.long
    )
    
    return Data(x=x, edge_index=edge_index, y=y)
