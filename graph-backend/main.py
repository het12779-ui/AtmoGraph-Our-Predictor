import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase

class RiskUpdate(BaseModel):
    risk: str  # "low" | "medium" | "high"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "atmograph123")

driver = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Connected to Neo4j successfully.")
    except Exception as e:
        print(f"Warning: Could not connect to Neo4j on startup: {e}")
        driver = None
    yield
    if driver:
        driver.close()
        print("Neo4j driver closed.")

app = FastAPI(title="AtmoGraph Predictor Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def set_risk(tx, node_id: str, risk: str):
    result = tx.run(
        "MATCH (n) WHERE n.id = $id SET n.risk = $risk RETURN n.id AS id, n.risk AS risk",
        id=node_id,
        risk=risk
    )
    return result.single()

def get_neighbors(tx, node_id, hops):
    query = (
        f"MATCH (n {{id: $id}})-[*1..{hops}]-(neighbor) "
        f"RETURN DISTINCT neighbor.id AS id, neighbor.name AS name, "
        f"coalesce(neighbor.risk, 'low') AS risk"
    )
    result = tx.run(query, id=node_id)
    return [dict(r) for r in result]

@app.get("/")
def read_root():
    return {"message": "AtmoGraph Backend API is running."}

@app.get("/graph")
def get_graph():
    if driver:
        try:
            with driver.session() as session:
                nodes_query = """
                MATCH (n)
                RETURN n.id AS id, coalesce(n.name, n.label, n.id) AS label, labels(n)[0] AS type, coalesce(n.risk, 'low') AS risk
                """
                nodes_result = session.run(nodes_query)
                nodes = []
                for r in nodes_result:
                    nodes.append({
                        "id": r["id"],
                        "label": r["label"] or r["id"],
                        "type": r["type"] or "Unknown",
                        "risk": r["risk"] or "low"
                    })

                edges_query = """
                MATCH (a)-[r]->(b)
                RETURN a.id AS source, b.id AS target, elementId(r) AS edge_id
                """
                edges_result = session.run(edges_query)
                edges = []
                for r in edges_result:
                    edges.append({
                        "id": r["edge_id"] or f"{r['source']}-{r['target']}",
                        "source": r["source"],
                        "target": r["target"]
                    })

                if nodes or edges:
                    return {"nodes": nodes, "edges": edges}
        except Exception as e:
            print(f"Neo4j query error: {e}")

    # Fallback mock graph if Neo4j is not populated or offline
    return {
        "nodes": [
            { "id": "1", "label": "Port of Rotterdam", "type": "Port", "risk": "low" },
            { "id": "2", "label": "Freight Co. X", "type": "Supplier", "risk": "medium" },
            { "id": "3", "label": "Factory (Ohio)", "type": "Manufacturer", "risk": "low" }
        ],
        "edges": [
            { "id": "e1-2", "source": "1", "target": "2" },
            { "id": "e2-3", "source": "2", "target": "3" }
        ]
    }

@app.patch("/node/{node_id}/risk")
def update_risk(node_id: str, payload: RiskUpdate):
    if driver:
        try:
            with driver.session() as session:
                record = session.execute_write(set_risk, node_id, payload.risk)
                if record:
                    return {
                        "message": "Risk updated successfully",
                        "id": record["id"],
                        "risk": record["risk"]
                    }
        except Exception as e:
            print(f"Neo4j update error: {e}")

    # Fallback response if offline
    return {
        "message": "Risk updated successfully (mock)",
        "id": node_id,
        "risk": payload.risk
    }

@app.get("/node/{node_id}/neighbors")
def node_neighbors(node_id: str, hops: int = 2):
    if driver:
        try:
            with driver.session() as session:
                neighbors = session.execute_read(
                    get_neighbors,
                    node_id,
                    hops
                )
                return {
                    "node_id": node_id,
                    "hops": hops,
                    "neighbors": neighbors
                }
        except Exception as e:
            print(f"Neo4j neighbors query error: {e}")

    # Fallback mock neighbors
    mock_neighbors_map = {
        "1": [{"id": "2", "name": "Freight Co. X", "risk": "medium"}, {"id": "3", "name": "Factory (Ohio)", "risk": "low"}],
        "2": [{"id": "1", "name": "Port of Rotterdam", "risk": "low"}, {"id": "3", "name": "Factory (Ohio)", "risk": "low"}],
        "3": [{"id": "2", "name": "Freight Co. X", "risk": "medium"}, {"id": "1", "name": "Port of Rotterdam", "risk": "low"}],
    }
    neighbors = mock_neighbors_map.get(node_id, [])
    return {
        "node_id": node_id,
        "hops": hops,
        "neighbors": neighbors
    }

