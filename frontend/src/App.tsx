import { useState, useMemo } from "react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import graphData from "./mock/graphData.json";
const TYPE_COLORS: Record<string, string> = {
Port: "#3b82f6",
Supplier: "#f59e0b",
Manufacturer: "#10b981",
Retailer: "#8b5cf6",
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
export default function App() {
const [selected, setSelected] = useState<Node | null>(null);
const [hiddenTypes, setHiddenTypes] = useState<Set<string>>(new Set());
const visibleNodes = useMemo(
() => allNodes.filter((n) => !hiddenTypes.has(String(n.data.type))),
[hiddenTypes]
);
const toggleType = (type: string) => {
setHiddenTypes((prev) => {
const next = new Set(prev);
next.has(type) ? next.delete(type) : next.add(type);
return next;
});
};

return (
<div style={{ width: "100vw", height: "100vh", display: "flex" }}>
<aside style={{ width: 180, padding: 16, borderRight: "1px solid #ccc" }}>
<h4>Node types</h4>
{Object.entries(TYPE_COLORS).map(([type, color]) => (
<label key={type} style={{ display: "block", marginBottom: 6 }}>
<input
type="checkbox"
checked={!hiddenTypes.has(type)}
onChange={() => toggleType(type)}
/>
<span style={{ color, marginLeft: 6 }}>■</span> {type}
</label>
))}
</aside>
<div style={{ flex: 1 }}>
<ReactFlow
nodes={visibleNodes}
edges={edges}
onNodeClick={(_, node) => setSelected(node)}
fitView
>
<Background />
<Controls />
<MiniMap nodeColor={(n) => TYPE_COLORS[String(n.data.type)] ?? "#999"} />
</ReactFlow>
</div>
{selected && (
<aside style={{ width: 240, padding: 16, borderLeft: "1px solid #ccc" }}>
<h3>{String(selected.data.label)}</h3>
<p>Type: {String(selected.data.type)}</p>
<p>Risk: {String(selected.data.risk)}</p>
</aside>
)}
</div>
);
}