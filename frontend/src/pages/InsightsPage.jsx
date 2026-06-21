import { useEffect, useState } from "react";
import { insightsAPI, suggestionsAPI } from "../services/api";
import { SEVERITY_COLORS } from "../utils/formatters";

const SEVERITY_LABELS = {
    high: "HIGH",
    medium: "MEDIUM",
    warning: "MEDIUM",
    info: "INFO",
    low: "INFO",
};

export default function InsightsPage() {
    const [insights, setInsights] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([insightsAPI.list(), suggestionsAPI.list()])
            .then(([insightsRes, suggestionsRes]) => {
                setInsights(insightsRes.data.insights || []);
                setSuggestions(suggestionsRes.data.suggestions || []);
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div style={{ padding: 40, color: "#475569", fontFamily: "monospace" }}>Loading...</div>
    );

    return (
        <div style={{ padding: 32, fontFamily: "monospace" }}>
            <h2 style={{ color: "#f1f5f9", margin: "0 0 8px", fontSize: 20 }}>Insights & Suggestions</h2>
            <p style={{ color: "#475569", fontSize: 13, margin: "0 0 32px" }}>
                Behavioral patterns and data-driven recommendations
            </p>

            <div style={{ marginBottom: 40 }}>
                <div style={{ fontSize: 11, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 16 }}>
                    Behavioral Insights ({insights.length})
                </div>

                {insights.length === 0 ? (
                    <div style={{ color: "#334155", fontSize: 13, padding: 20, background: "#0d1117", borderRadius: 8, border: "1px solid #1e2d3d" }}>
                        No notable patterns detected yet.
                    </div>
                ) : (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        {insights.map((insight, i) => {
                            const color = SEVERITY_COLORS[insight.severity] || SEVERITY_COLORS.info;
                            return (
                                <div key={i} style={{
                                    background: "#0d1117", border: `1px solid ${color}30`,
                                    borderLeft: `3px solid ${color}`, borderRadius: 8,
                                    padding: "16px 20px",
                                }}>
                                    <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 500, marginBottom: 6 }}>
                                        {insight.message}
                                    </div>
                                    {insight.sub && (
                                        <div style={{ fontSize: 12, color: "#64748b" }}>{insight.sub}</div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <div>
                <div style={{ fontSize: 11, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 16 }}>
                    Suggestions ({suggestions.length})
                </div>

                {suggestions.length === 0 ? (
                    <div style={{ color: "#334155", fontSize: 13, padding: 20, background: "#0d1117", borderRadius: 8, border: "1px solid #1e2d3d" }}>
                        No suggestions right now — spending looks balanced.
                    </div>
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                        {suggestions.map((s, i) => {
                            const color = SEVERITY_COLORS[s.severity] || SEVERITY_COLORS.info;
                            return (
                                <div key={i} style={{
                                    background: "#0d1117", border: `1px solid ${color}30`,
                                    borderRadius: 8, padding: "16px 20px",
                                }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8, gap: 12 }}>
                                        <div style={{ fontSize: 13, color: "#f1f5f9", fontWeight: 600 }}>{s.title}</div>
                                        <span style={{
                                            fontSize: 9, padding: "2px 8px", borderRadius: 3,
                                            background: `${color}18`, color,
                                            border: `1px solid ${color}40`, letterSpacing: "0.1em",
                                            flexShrink: 0,
                                        }}>
                                            {SEVERITY_LABELS[s.severity] || "INFO"}
                                        </span>
                                    </div>
                                    <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8, lineHeight: 1.6 }}>
                                        {s.message}
                                    </div>
                                    <div style={{ fontSize: 12, color: "#00ff9d", display: "flex", gap: 6 }}>
                                        <span>→</span>
                                        <span>{s.recommendation}</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}