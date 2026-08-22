import socket
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, DriverError

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")

def load_relationships(tx, df, rel_type="SUPPLIES", src_col="node1", dst_col="node2"):
    for _, row in df.iterrows():
        src_id = str(row.get(src_col, row.get("Plant", row.get("plant_id"))))
        dst_id = str(row.get(dst_col, row.get("Node", row.get("product_id"))))
        if src_id and dst_id and src_id != "nan" and dst_id != "nan":
            tx.run(
                f"MATCH (a {{id: $src_id}}), (b {{id: $dst_id}}) "
                f"MERGE (a)-[:{rel_type}]->(b)",
                src_id=src_id,
                dst_id=dst_id,
            )

def load_plant_storage_mappings(tx, df):
    for _, row in df.iterrows():
        product_id = str(row.get("Node", ""))
        plant_id = str(row.get("Plant", ""))
        storage_id = str(row.get("Storage Location", ""))
        
        if plant_id and plant_id != "nan" and product_id and product_id != "nan":
            tx.run(
                "MATCH (m:Manufacturer {id: $plant_id}), (p:Product {id: $product_id}) "
                "MERGE (m)-[:SUPPLIES]->(p)",
                plant_id=plant_id, product_id=product_id
            )
        if storage_id and storage_id != "nan" and product_id and product_id != "nan":
            tx.run(
                "MATCH (s:Port {id: $storage_id}), (p:Product {id: $product_id}) "
                "MERGE (s)-[:SHIPS_VIA]->(p)",
                storage_id=storage_id, product_id=product_id
            )

def is_neo4j_reachable(host="localhost", port=7687, timeout=2):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False

if __name__ == "__main__":
    if not is_neo4j_reachable():
        print(f"Could not connect to Neo4j database at {URI}.")
        print("Ensure Neo4j container is running via `docker-compose up -d`.")
    else:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        raw = Path("data/raw")
        with driver.session() as session:
            for csv_file in raw.rglob("*.csv"):
                if "edgesindex" in str(csv_file).lower():
                    continue
                filename = csv_file.name.lower()
                df = pd.read_csv(csv_file)
                if "plant & storage" in filename:
                    print(f"Loading plant & storage relationships from {csv_file.name} ({len(df)} rows)...")
                    session.execute_write(load_plant_storage_mappings, df)
                elif "edges (plant)" in filename:
                    print(f"Loading plant relationships from {csv_file.name} ({len(df)} rows)...")
                    session.execute_write(load_relationships, df, rel_type="SUPPLIES", src_col="node1", dst_col="node2")
                elif "edges (storage location)" in filename:
                    print(f"Loading storage relationships from {csv_file.name} ({len(df)} rows)...")
                    session.execute_write(load_relationships, df, rel_type="SHIPS_VIA", src_col="node1", dst_col="node2")
                elif "product group" in filename or "product sub-group" in filename:
                    if "edges" in filename:
                        print(f"Loading group/subgroup dependencies from {csv_file.name} ({len(df)} rows)...")
                        session.execute_write(load_relationships, df, rel_type="DEPENDS_ON", src_col="node1", dst_col="node2")
        driver.close()
        print("Edge load complete.")
