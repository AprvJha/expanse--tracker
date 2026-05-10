// frontend/src/components/UI/StatCard.jsx
export default function StatCard({ label, value, sub, color = "#00ff9d" }) {
    return (
        <div style={{
            background: "#0d1117", border: "1px solid #1e2d3d",
            borderRadius: 8, padding: "20px 24px",
        }}>
            <div style={{ fontSize: 11, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 8 }}>
                {label}
            </div>
            <div style={{ fontSize: 28, fontWeight: 700, color, marginBottom: 4, fontFamily: "monospace" }}>
                {value}
            </div>
            {sub && <div style={{ fontSize: 12, color: "#334155" }}>{sub}</div>}
        </div>
    );
}