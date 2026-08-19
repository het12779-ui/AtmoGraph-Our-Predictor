cat > src/App.tsx << 'EOF'
import { useState } from "react";
import ReactFlow, { Background, Controls, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import graphData from "./mock/graphData.json";
const nodes: Node[] = graphData.nodes.map((n, i) => ({
id: n.id,
position: { x: i * 200, y: (i % 2) * 100 },
data: { label: n.label, type: n.type, risk: n.risk },
}));
const edges: Edge[] = graphData.edges.map((e) => ({
id: e.id, source: e.source, target: e.target, animated: true,
}));
export default function App() {
const [selected, setSelected] = useState<Node | null>(null);
return (
<div style={{ width: "100vw", height: "100vh", display: "flex" }}>
<div style={{ flex: 1 }}>
<ReactFlow
nodes={nodes}
edges={edges}
onNodeClick={(_, node) => setSelected(node)}
fitView
>
<Background />
<Controls />
</ReactFlow>
</div>
{selected && (
<aside style={{ width: 260, padding: 16, borderLeft: "1px solid #ccc" }}>
<h3>{String(selected.data.label)}</h3>
<p>Type: {String(selected.data.type)}</p>
<p>Risk: {String(selected.data.risk)}</p>
</aside>
)}
</div>
);
}
EOF