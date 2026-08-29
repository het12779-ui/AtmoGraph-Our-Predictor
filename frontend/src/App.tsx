import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import { fetchGraph, GraphResponse } from "./api";
const RISK_COLORS: Record<string, string> = {
low: "#10b981", medium: "#f59e0b", high: "#ef4444",
};
export default function App() {
const [data, setData] = useState<GraphResponse | null>(null);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
fetchGraph().then(setData).catch((e) => setError(e.message));
}, []);
if (error) return <div style={{ padding: 40, color: "red" }}>Failed to load graph: {error}</div>;
if (!data) return <div style={{ padding: 40 }}>Loading graph from backend...</div>;
const nodes: Node[] = data.nodes.map((n, i) => ({
id: n.id,
position: { x: (i % 5) * 180, y: Math.floor(i / 5) * 120 },
data: { label: n.label, risk: n.risk },
style: { background: RISK_COLORS[n.risk] ?? "#999", color: "#fff", borderRadius: 6 },
}));
const edges: Edge[] = data.edges.map((e) => ({
id: `${e.source}-${e.target}`, source: e.source, target: e.target, animated: true,
}));
return (
<div style={{ width: "100vw", height: "100vh" }}>
<ReactFlow nodes={nodes} edges={edges} fitView>
<Background /><Controls /><MiniMap nodeColor={(n) => RISK_COLORS[String(n.data.risk)] ?? "#999"} />
</ReactFlow>
</div>
);
}