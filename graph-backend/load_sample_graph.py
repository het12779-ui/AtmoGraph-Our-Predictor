import socket
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, DriverError

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")

SAMPLE_NODES = [
    {"id": "supplier_1", "type": "Supplier", "name": "Acme Components"},
    {"id": "port_1", "type": "Port", "name": "Port of Rotterdam"},
    {"id": "mfg_1", "type": "Manufacturer", "name": "Global Electronics Co."},
    {"id": "retailer_1", "type": "Retailer", "name": "US Retail Corp"},
]

SAMPLE_EDGES = [
    ("supplier_1", "SHIPS_VIA", "port_1"),
    ("port_1", "SUPPLIES", "mfg_1"),
    ("mfg_1", "SUPPLIES", "retailer_1"),
]

def load(tx):
    for n in SAMPLE_NODES:
        tx.run(
            f"MERGE (n:{n['type']} {{id: $id}}) SET n.name = $name",
            id=n["id"], name=n["name"],
        )
    for src, rel, dst in SAMPLE_EDGES:
        tx.run(
            f"MATCH (a {{id: $src}}), (b {{id: $dst}}) MERGE (a)-[:{rel}]->(b)",
            src=src, dst=dst,
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
        try:
            driver = GraphDatabase.driver(URI, auth=AUTH)
            with driver.session() as session:
                session.execute_write(load)
            driver.close()
            print("Sample graph loaded. Open http://localhost:7474 and run: MATCH (n) RETURN n")
        except (ServiceUnavailable, DriverError, OSError) as e:
            print(f"Could not connect to Neo4j database at {URI}: {e}")
            print("Ensure Neo4j container is running via `docker-compose up -d`.")
