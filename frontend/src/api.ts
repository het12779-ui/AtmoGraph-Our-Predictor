export interface GraphNode {
  id: string;
  label: string;
  type: string;
  risk: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export async function fetchGraph(): Promise<GraphResponse> {
  const res = await fetch("http://localhost:8000/graph");
  if (!res.ok) throw new Error(`Graph fetch failed: ${res.status}`);
  return res.json();
}

export async function updateNodeRisk(nodeId: string, risk: string): Promise<void> {
  const res = await fetch(`http://localhost:8000/node/${nodeId}/risk`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ risk }),
  });
  if (!res.ok) throw new Error(`Risk update failed: ${res.status}`);
}

export interface NeighborsResponse {
  node_id: string;
  hops: number;
  neighbors: { id: string; name: string; risk: string }[];
}

export async function fetchNeighbors(nodeId: string, hops = 2): Promise<NeighborsResponse> {
  const res = await fetch(`http://localhost:8000/node/${nodeId}/neighbors?hops=${hops}`);
  if (!res.ok) throw new Error(`Neighbors fetch failed: ${res.status}`);
  return res.json();
}