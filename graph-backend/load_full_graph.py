import socket
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, DriverError

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")

def load_products(tx, df):
    for _, row in df.iterrows():
        product_id = str(row.get("Node", row.get("product_id", row.get("id"))))
        group_name = str(row.get("Group", ""))
        subgroup_name = str(row.get("Sub-Group", ""))
        tx.run(
            """
            MERGE (p:Product {id: $id})
            SET p.name = $id,
                p.group = $group,
                p.subgroup = $subgroup
            """,
            id=product_id,
            group=group_name,
            subgroup=subgroup_name,
        )

def load_plants(tx, df):
    for _, row in df.iterrows():
        plant_id = str(row.get("Plant", row.get("plant_id", row.get("id"))))
        if plant_id and plant_id != "nan":
            tx.run(
                "MERGE (m:Manufacturer {id: $id}) SET m.name = $name",
                id=plant_id,
                name=f"Plant_{plant_id}",
            )

def load_storage(tx, df):
    for _, row in df.iterrows():
        storage_id = str(row.get("Storage Location", row.get("storage_id", row.get("id"))))
        if storage_id and storage_id != "nan":
            tx.run(
                "MERGE (p:Port {id: $id}) SET p.name = $name",
                id=storage_id,
                name=f"Storage_{storage_id}",
            )

def load_plant_edges(tx, df):
    for _, row in df.iterrows():
        src = str(row.get("node1"))
        dst = str(row.get("node2"))
        plant = str(row.get("Plant", ""))
        tx.run(
            """
            MATCH (a {id: $src}), (b {id: $dst})
            MERGE (a)-[r:PLANT_RELATION {plant: $plant}]->(b)
            """,
            src=src, dst=dst, plant=plant
        )

def load_storage_edges(tx, df):
    for _, row in df.iterrows():
        src = str(row.get("node1"))
        dst = str(row.get("node2"))
        storage = str(row.get("Storage Location", ""))
        tx.run(
            """
            MATCH (a {id: $src}), (b {id: $dst})
            MERGE (a)-[r:STORAGE_RELATION {storage: $storage}]->(b)
            """,
            src=src, dst=dst, storage=storage
        )

def load_group_edges(tx, df):
    for _, row in df.iterrows():
        src = str(row.get("node1"))
        dst = str(row.get("node2"))
        group = str(row.get("GroupCode", ""))
        tx.run(
            """
            MATCH (a {id: $src}), (b {id: $dst})
            MERGE (a)-[r:PRODUCT_GROUP_RELATION {group: $group}]->(b)
            """,
            src=src, dst=dst, group=group
        )

def load_subgroup_edges(tx, df):
    for _, row in df.iterrows():
        src = str(row.get("node1"))
        dst = str(row.get("node2"))
        subgroup = str(row.get("SubGroupCode", ""))
        tx.run(
            """
            MATCH (a {id: $src}), (b {id: $dst})
            MERGE (a)-[r:PRODUCT_SUBGROUP_RELATION {subgroup: $subgroup}]->(b)
            """,
            src=src, dst=dst, subgroup=subgroup
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
                df = pd.read_csv(csv_file)
                print(f"Loading {csv_file.name} ({len(df)} rows)...")
                filename = csv_file.name.lower()
                if "nodes" in filename or "product group and subgroup" in filename:
                    if "plant & storage" in filename:
                        session.execute_write(load_plants, df)
                        session.execute_write(load_storage, df)
                    else:
                        session.execute_write(load_products, df)
                elif "edges (plant)" in filename:
                    session.execute_write(load_plant_edges, df)
                elif "edges (storage location)" in filename:
                    session.execute_write(load_storage_edges, df)
                elif "edges (product group)" in filename:
                    session.execute_write(load_group_edges, df)
                elif "edges (product sub-group)" in filename:
                    session.execute_write(load_subgroup_edges, df)
        driver.close()
        print("Bulk load complete. Verify counts in Neo4j Browser next.")
