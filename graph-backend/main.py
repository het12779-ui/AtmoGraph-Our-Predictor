
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "atmograph123")

driver = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    try:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully.")
    except Exception as e:
        print(f"Warning: Could not connect to Neo4j on startup: {e}")

    yield

    if driver:
        driver.close()
        print("Neo4j driver closed.")


app = FastAPI(
    title="AtmoGraph Predictor Backend",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RiskUpdate(BaseModel):
    risk: str


def set_risk(tx, node_id: str, risk: str):
    result = tx.run(
        """
        MATCH (n)
        WHERE n.id = $id
        SET n.risk = $risk
        RETURN n.id AS id, n.risk AS risk
        """,
        id=node_id,
        risk=risk
    )

    return result.single()


def get_neighbors(tx, node_id: str, hops: int):
    query = (
        f"MATCH (n {{id: $id}})-[*1..{hops}]-(neighbor) "
        f"RETURN DISTINCT "
        f"neighbor.id AS id, "
        f"neighbor.name AS name, "
        f"coalesce(neighbor.risk, 'low') AS risk"
    )

    result = tx.run(query, id=node_id)

    return [dict(r) for r in result]


def get_neighbors_with_distance(tx, node_id: str, hops: int):
    query = (
        f"MATCH (n {{id: $id}}) "
        f"MATCH p = shortestPath((n)-[*1..{hops}]-(neighbor)) "
        f"WHERE neighbor.id <> $id "
        f"RETURN DISTINCT "
        f"neighbor.id AS id, "
        f"neighbor.name AS name, "
        f"coalesce(neighbor.risk, 'low') AS risk, "
        f"length(p) AS hops_away"
    )

    result = tx.run(query, id=node_id)

    return [dict(r) for r in result]


DECAY_PER_HOP = 0.5


@app.get("/")
def read_root():
    return {
        "message": "AtmoGraph Backend API is running."
    }


@app.get("/graph")
def get_graph():

    if not driver:
        raise HTTPException(
            status_code=500,
            detail="Neo4j driver is not initialized."
        )

    try:
        with driver.session() as session:

            nodes_query = """
            MATCH (n)
            RETURN
                n.id AS id,
                n.name AS label,
                labels(n)[0] AS type,
                n.risk AS risk
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
            RETURN
                a.id AS source,
                b.id AS target,
                elementId(r) AS edge_id
            """

            edges_result = session.run(edges_query)

            edges = []

            for r in edges_result:
                edges.append({
                    "id": r["edge_id"] or f"{r['source']}-{r['target']}",
                    "source": r["source"],
                    "target": r["target"]
                })

            return {
                "nodes": nodes,
                "edges": edges
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        )


@app.patch("/node/{node_id}/risk")
def update_risk(node_id: str, payload: RiskUpdate):

    if not driver:
        raise HTTPException(
            status_code=500,
            detail="Neo4j driver is not initialized."
        )

    try:
        with driver.session() as session:

            record = session.execute_write(
                set_risk,
                node_id,
                payload.risk
            )

            if not record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Node with id '{node_id}' not found"
                )

            return {
                "message": "Risk updated successfully",
                "id": record["id"],
                "risk": record["risk"]
            }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database update failed: {str(e)}"
        )


@app.get("/node/{node_id}/neighbors")
def node_neighbors(node_id: str, hops: int = 2):

    if not driver:
        raise HTTPException(
            status_code=500,
            detail="Neo4j driver is not initialized."
        )

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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get neighbors: {str(e)}"
        )


@app.get("/node/{node_id}/impact")
def node_impact(node_id: str, hops: int = 3):

    if not driver:
        raise HTTPException(
            status_code=500,
            detail="Neo4j driver is not initialized."
        )

    try:
        with driver.session() as session:

            neighbors = session.execute_read(
                get_neighbors_with_distance,
                node_id,
                hops
            )

        for n in neighbors:
            n["impact_score"] = round(
                DECAY_PER_HOP ** (n["hops_away"] - 1),
                3
            )

        return {
            "node_id": node_id,
            "hops": hops,
            "neighbors": neighbors
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate node impact: {str(e)}"
        )

