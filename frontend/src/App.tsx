import { useState, useMemo } from "react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge, useReactFlow, ReactFlowProvider } from "reactflow";
import "reactflow/dist/style.css";
import graphData from "./mock/graphData.json";
const TYPE_COLORS: Record<string, string> = {
Port: "#3b82f6", Supplier: "#f59e0b", Manufacturer: "#10b981", Retailer: "#8b5cf6",
};
const allNodes: Node[] = graphData.nodes.map((n, i) => ({
id: n.id,
position: { x: i * 200, y: (i % 2) * 100 },
data: { label: n.label, type: n.type, risk: n.risk },
style: { background: TYPE_COLORS[n.type] ?? "#999", color: "#fff", borderRadius: 6 },
}));
const edges: Edge[] = graphData.edges.map((e) => ({
id: e.id, source: e.source, target: e.target, animated: true,
}));
function Dashboard() {
const [selected, setSelected] = useState<Node | null>(null);
const [query, setQuery] = useState("");
const { setCenter } = useReactFlow();
const isLoading = false; // Week 2: wire this to a real fetch() loading state
const isEmpty = allNodes.length === 0;
const handleSearch = () => {
const match = allNodes.find((n) =>
String(n.data.label).toLowerCase().includes(query.toLowerCase())
);
if (match) {
setSelected(match);
setCenter(match.position.x, match.position.y, { zoom: 1.2, duration: 500 });
}
};

if (isEmpty) {
return <div style={{ padding: 40 }}>No graph data yet — check back once the backend is connected.</div>;
}
return (
<div style={{ width: "100vw", height: "100vh", display: "flex" }}>
<aside style={{ width: 200, padding: 16, borderRight: "1px solid #ccc" }}>
<input
value={query}
onChange={(e) => setQuery(e.target.value)}
onKeyDown={(e) => e.key === "Enter" && handleSearch()}
placeholder="Search node..."
style={{ width: "100%", padding: 6, marginBottom: 12 }}
/>
{Object.entries(TYPE_COLORS).map(([type, color]) => (
<div key={type} style={{ marginBottom: 4 }}>
<span style={{ color }}>■</span> {type}
</div>
))}
</aside>
<div style={{ flex: 1, position: "relative" }}>
{isLoading && <div style={{ position: "absolute", zIndex: 10, padding: 16 }}>Loading...</div>}
<ReactFlow nodes={allNodes} edges={edges} onNodeClick={(_, n) => setSelected(n)} fitView>
<Background /><Controls />
<MiniMap nodeColor={(n) => TYPE_COLORS[String(n.data.type)] ?? "#999"} />
</ReactFlow>
</div>
{selected && (
<aside style={{ width: 240, padding: 16, borderLeft: "1px solid #ccc" }}>
<h3>{String(selected.data.label)}</h3>
<p>Type: {String(selected.data.type)}</p>
</aside>
)}
</div>
);
}
export default function App() {
return (
<ReactFlowProvider>
<Dashboard />
</ReactFlowProvider>
);
}