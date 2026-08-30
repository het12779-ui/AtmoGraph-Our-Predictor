import { useState, useEffect } from "react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import { fetchGraph, updateNodeRisk, fetchNeighbors, GraphResponse } from "./api";

const RISK_COLORS: Record<string, string> = {
  low: "#10b981",
  medium: "#f59e0b",
  high: "#ef4444",
};

export default function App() {
  const [data, setData] = useState<GraphResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Node | null>(null);
  const [highlighted, setHighlighted] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchGraph().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div style={{ padding: 40, color: "red" }}>Failed to load graph: {error}</div>;
  if (!data) return <div style={{ padding: 40 }}>Loading graph from backend...</div>;

  const nodes: Node[] = data.nodes.map((n, i) => ({
    id: n.id,
    position: { x: (i % 5) * 180, y: Math.floor(i / 5) * 120 },
    data: { label: n.label, risk: n.risk, type: n.type },
    style: {
      background: RISK_COLORS[n.risk] ?? "#999",
      color: "#fff",
      borderRadius: 6,
      padding: "8px",
      border: highlighted.has(n.id) ? "3px solid red" : undefined,
    },
  }));

  const edges: Edge[] = data.edges.map((e) => ({
    id: `${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    animated: true,
  }));

  return (
    <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={(_event, node) => setSelected(node)}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap nodeColor={(n) => RISK_COLORS[String(n.data.risk)] ?? "#999"} />
      </ReactFlow>

      {selected && (
        <aside
          style={{
            position: "absolute",
            top: 20,
            right: 20,
            width: 280,
            background: "#ffffff",
            border: "1px solid #e5e7eb",
            borderRadius: 8,
            padding: 16,
            boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)",
            zIndex: 10,
            color: "#1f2937",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Node Details</h3>
            <button
              onClick={() => setSelected(null)}
              style={{
                border: "none",
                background: "transparent",
                cursor: "pointer",
                fontSize: 16,
                color: "#6b7280",
              }}
            >
              ✕
            </button>
          </div>
          <div style={{ marginBottom: 8 }}>
            <strong>ID:</strong> {selected.id}
          </div>
          <div style={{ marginBottom: 8 }}>
            <strong>Label:</strong> {selected.data.label}
          </div>
          <div style={{ marginBottom: 8 }}>
            <strong>Type:</strong> {selected.data.type || "N/A"}
          </div>
          <div style={{ marginBottom: 12 }}>
            <strong>Current Risk:</strong>{" "}
            <span
              style={{
                display: "inline-block",
                padding: "2px 8px",
                borderRadius: 4,
                color: "#fff",
                fontSize: 12,
                fontWeight: 600,
                background: RISK_COLORS[selected.data.risk] ?? "#999",
              }}
            >
              {selected.data.risk}
            </span>
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <select
              id="risk-select"
              key={selected.id}
              defaultValue={selected.data.risk}
              style={{
                padding: "6px 10px",
                borderRadius: 4,
                border: "1px solid #d1d5db",
                flex: 1,
              }}
            >
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
            <button
              onClick={async () => {
                const value = (document.getElementById("risk-select") as HTMLSelectElement).value;
                await updateNodeRisk(selected.id, value);
                const { neighbors } = await fetchNeighbors(selected.id, 2);
                setHighlighted(new Set(neighbors.map((n) => n.id)));
                alert(`Set ${selected.data.label} to ${value}. Highlighted ${neighbors.length} affected node(s).`);
              }}
              style={{
                padding: "6px 12px",
                background: "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
                fontWeight: 500,
              }}
            >
              Simulate disruption
            </button>
          </div>
        </aside>
      )}
    </div>
  );
}