// frontend/src/pages/AnomaliesPage.jsx
import { useEffect, useState } from "react";
import { anomalyAPI } from "../services/api";
import { formatCurrency, SEVERITY_COLORS } from "../utils/formatters";

export default function AnomaliesPage() {
    const [metrics, setMetrics] = useState(null);
    const [detection, setDetection] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([anomalyAPI.metrics(), anomalyAPI.detect()])
            .then(([metricsRes, detectRes]) => {
                setMetrics(metricsRes.data);
                setDetection(detectRes.data);
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div style={{ padding: 40, color: "#475569", fontFamily: "monospace" }}>Loading...</div>
    );

    const hasMetrics = metrics?.zscore && metrics?.isolation_forest;

    return (
        <div style={{ padding: 32, fontFamily: "monospace" }}>
            <h2 style={{ color: "#f1f5f9", margin: "0 0 8px", fontSize: 20 }}>Anomaly Detection</h2>
            <p style={{ color: "#475569", fontSize: 13, margin: "0 0 32px" }}>
                Two-tier detection: Z-score + Isolation Forest, evaluated on labeled test data
            </p>

            {/* Model metrics */}
            {hasMetrics ? (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
                    {[
                        { name: "Z-Score", data: metrics.zscore, color: "#38bdf8" },
                        { name: "Isolation Forest", data: metrics.isolation_forest, color: "#a78bfa" },
                    ].map((m) => (
                        <div key={m.name} style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 24 }}>
                            <div style={{ fontSize: 12, color: m.color, marginBottom: 16, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                                {m.name}
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                                {[
                                    { label: "Precision", value: m.data.precision },
                                    { label: "Recall", value: m.data.recall },
                                    { label: "F1 Score", value: m.data.f1 },
                                ].map((stat) => (
                                    <div key={stat.label}>
                                        <div style={{ fontSize: 24, color: "#f1f5f9", fontWeight: 700 }}>
                                            {(stat.value * 100).toFixed(0)}%
                                        </div>
                                        <div style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                                            {stat.label}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div style={{ marginTop: 12, fontSize: 11, color: "#334155" }}>
                                {m.data.true_positives} true positives · {m.data.total_flagged} flagged
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div style={{ color: "#64748b", fontSize: 13, padding: 24, background: "#0d1117", borderRadius: 8, border: "1px solid #1e2d3d", marginBottom: 24, textAlign: "center" }}>
                    {metrics?.message || "No labeled anomaly data available. Add expenses with labeled anomalies to see model evaluation metrics."}
                </div>
            )}

            {/* Summary stats */}
            {detection && (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
                    {[
                        { label: "Total Transactions", value: detection.total_transactions, color: "#00ff9d" },
                        { label: "Anomalies Detected", value: detection.anomalies_detected, color: "#f43f5e" },
                        { label: "High Severity", value: detection.high, color: "#f43f5e" },
                        { label: "Medium / Low", value: detection.medium + detection.low, color: "#facc15" },
                    ].map((s) => (
                        <div key={s.label} style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: "16px 20px" }}>
                            <div style={{ fontSize: 22, color: s.color, fontWeight: 700, marginBottom: 4 }}>{s.value}</div>
                            <div style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>{s.label}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* Anomaly table */}
            <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, overflow: "hidden" }}>
                <div style={{
                    display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 100px 2fr",
                    padding: "12px 20px", background: "#090d12", borderBottom: "1px solid #1e2d3d",
                }}>
                    {["Merchant", "Category", "Amount", "Severity", "Detail"].map((h) => (
                        <span key={h} style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>{h}</span>
                    ))}
                </div>

                <div style={{ maxHeight: 400, overflowY: "auto" }}>
                    {(!detection || detection.alerts.length === 0) ? (
                        <div style={{ padding: 40, textAlign: "center", color: "#475569" }}>No anomalies detected</div>
                    ) : detection.alerts.map((alert, i) => {
                        const color = SEVERITY_COLORS[alert.severity] || "#38bdf8";
                        return (
                            <div key={i} style={{
                                display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 100px 2fr",
                                padding: "14px 20px", borderBottom: "1px solid #0f1923", alignItems: "center",
                            }}>
                                <div style={{ fontSize: 13, color: "#e2e8f0" }}>{alert.merchant}</div>
                                <div style={{ fontSize: 12, color: "#64748b" }}>{alert.category}</div>
                                <div style={{ fontSize: 13, color: "#f1f5f9", fontWeight: 500 }}>{formatCurrency(alert.amount)}</div>
                                <div>
                                    <span style={{
                                        fontSize: 10, padding: "3px 10px", borderRadius: 4,
                                        background: `${color}18`, color,
                                        border: `1px solid ${color}40`,
                                        textTransform: "uppercase", letterSpacing: "0.1em",
                                    }}>
                                        {alert.severity}
                                    </span>
                                </div>
                                <div style={{ fontSize: 11, color: "#475569" }}>{alert.message}</div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}