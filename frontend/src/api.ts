export interface GraphNode {
id: string; label: string; type: string; risk: string;
}
export interface GraphEdge {
id: string; source: string; target: string;
}
export interface GraphResponse {
nodes: GraphNode[]; edges: GraphEdge[];
}
export async function fetchGraph(): Promise<GraphResponse> {
const res = await fetch("http://localhost:8000/graph");
if (!res.ok) throw new Error(`Graph fetch failed: ${res.status}`);
return res.json();
}