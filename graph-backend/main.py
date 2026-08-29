import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
from pydantic import BaseModel


class RiskUpdate(BaseModel):
    risk: str  # "low" | "medium" | "high"


def set_risk(tx, node_id, risk):
    tx.run(
        "MATCH (n {id: $id}) SET n.risk = $risk",
        id=node_id,
        risk=risk
    )


@app.patch("/node/{node_id}/risk")
def update_risk(node_id: str, update: RiskUpdate):
    with driver.session() as session:
        session.execute_write(
            set_risk,
            node_id,
            update.risk
        )

    return {
        "id": node_id,
        "risk": update.risk
    }

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "atmograph123")

driver = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    # Test connection
    try:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully.")
    except Exception as e:
        print(f"Warning: Could not connect to Neo4j on startup: {e}")
    yield
    if driver:
        driver.close()
        print("Neo4j driver closed.")

app = FastAPI(title="AtmoGraph Predictor Backend", lifespan=lifespan)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RiskUpdate(BaseModel):
    risk: str  # "low" | "medium" | "high"

def set_risk(tx, node_id: str, risk: str):
    result = tx.run(
        "MATCH (n) WHERE n.id = $id SET n.risk = $risk RETURN n.id AS id, n.risk AS risk",
        id=node_id,
        risk=risk
    )
    return result.single()

@app.get("/")
def read_root():
    return {"message": "AtmoGraph Backend API is running."}

@app.get("/graph")
def get_graph():
    if not driver:
        raise HTTPException(status_code=500, detail="Neo4j driver is not initialized.")
    try:
        with driver.session() as session:
            # Query all nodes
            nodes_query = """
            MATCH (n)
            RETURN n.id AS id, n.name AS label, labels(n)[0] AS type, n.risk AS risk
            """
            nodes_result = session.run(nodes_query)
            nodes = []
            for r in nodes_result:
                # Fallbacks for missing optional properties
                nodes.append({
                    "id": r["id"],
                    "label": r["label"] or r["id"],
                    "type": r["type"] or "Unknown",
                    "risk": r["risk"] or "low"
                })

            # Query all edges
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

            return {"nodes": nodes, "edges": edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.patch("/node/{node_id}/risk")
def update_risk(node_id: str, payload: RiskUpdate):
    if not driver:
        raise HTTPException(status_code=500, detail="Neo4j driver is not initialized.")
    try:
        with driver.session() as session:
            record = session.execute_write(set_risk, node_id, payload.risk)
            if not record:
                raise HTTPException(status_code=404, detail=f"Node with id '{node_id}' not found")
            return {
                "message": "Risk updated successfully",
                "id": record["id"],
                "risk": record["risk"]
            }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
