import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Port of Rotterdam" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "Freight Co. X" } },
  { id: "3", position: { x: 400, y: 0 }, data: { label: "Factory (Ohio)" } },
];

const edges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true },
  { id: "e2-3", source: "2", target: "3", animated: true },
];

export default function App() {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <h2 style={{ position: "absolute", zIndex: 10, margin: 16 }}>
        AtmoGraph - Day 1 mock graph
      </h2>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
