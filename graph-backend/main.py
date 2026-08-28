from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from pydantic import BaseModel
import os

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "atmograph123"))

app = FastAPI(title="AtmoGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

driver = None

def get_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(URI, auth=AUTH, connection_timeout=2.0)
    return driver

class RiskUpdate(BaseModel):
    risk: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/graph")
def get_graph():
    try:
        drv = get_driver()
        with drv.session() as session:
            # Query nodes
            nodes_result = session.run("MATCH (n) RETURN n, labels(n) AS labels")
            nodes = []
            for record in nodes_result:
                node = record["n"]
                labels = record["labels"]
                node_id = str(node.get("id") or node.element_id)
                label = str(node.get("name") or node.get("label") or node_id)
                node_type = labels[0] if labels else "Unknown"
                risk = str(node.get("risk") or "low")
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "risk": risk
                })

            # Query edges
            edges_result = session.run("MATCH (a)-[r]->(b) RETURN r, a, b")
            edges = []
            for record in edges_result:
                rel = record["r"]
                a = record["a"]
                b = record["b"]
                edge_id = str(rel.get("id") or rel.element_id)
                source_id = str(a.get("id") or a.element_id)
                target_id = str(b.get("id") or b.element_id)
                edges.append({
                    "id": edge_id,
                    "source": source_id,
                    "target": target_id
                })

            # If graph is empty (e.g. database not populated yet), return default mock shape
            if not nodes and not edges:
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

            return {"nodes": nodes, "edges": edges}
    except Exception as e:
        # Fallback to mock graph if Neo4j is unreachable
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
def update_node_risk(node_id: str, update: RiskUpdate):
    try:
        drv = get_driver()
        with drv.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE n.id = $node_id OR elementId(n) = $node_id OR n.name = $node_id
                SET n.risk = $risk
                RETURN n
                """,
                node_id=node_id, risk=update.risk
            )
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
            return {"status": "ok", "node_id": node_id, "risk": update.risk}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
