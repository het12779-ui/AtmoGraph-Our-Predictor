import torch
from torch_geometric.data import Data
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")

def fetch_graph(tx, limit=200):
    result = tx.run(
        "MATCH (a)-[r]->(b) RETURN a.id AS src, b.id AS dst, labels(a)[0] AS src_type "
        "LIMIT $limit", limit=limit
    )
    return [(record["src"], record["dst"], record["src_type"]) for record in result]

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        edges = session.execute_read(fetch_graph)
    driver.close()
    
    if not edges:
        print("No edges found — make sure Het's Day 3 load_full_graph.py has been run first.")
        exit()
        
    # Build a node id -> index mapping
    node_ids = sorted({n for src, dst, _ in edges for n in (src, dst)})
    id_to_idx = {node_id: i for i, node_id in enumerate(node_ids)}
    src_idx = [id_to_idx[s] for s, d, _ in edges]
    dst_idx = [id_to_idx[d] for s, d, _ in edges]
    edge_index = torch.tensor([src_idx, dst_idx], dtype=torch.long)
    
    # Placeholder features for now — Week 2 replaces this with real criticality/risk features
    x = torch.ones((len(node_ids), 2), dtype=torch.float)
    data = Data(x=x, edge_index=edge_index)
    
    print(data)
    print(f"Converted {len(node_ids)} nodes and {len(edges)} edges from Neo4j into a PyG Data object.")
