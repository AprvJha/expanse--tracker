// frontend/src/pages/DashboardPage.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { expensesAPI, predictionAPI, suggestionsAPI } from "../services/api";
import StatCard from "../components/UI/StatCard";
import { formatCurrency, CATEGORY_COLORS, SEVERITY_COLORS } from "../utils/formatters";
import {
    PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
    AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from "recharts";

export default function DashboardPage() {
    const [summary, setSummary] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [topSuggestion, setTopSuggestion] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            expensesAPI.summary(),
            predictionAPI.forecast(30).catch(() => ({ data: null })),
            suggestionsAPI.list().catch(() => ({ data: null })),
        ]).then(([summaryRes, forecastRes, suggestionsRes]) => {
            setSummary(summaryRes.data);
            if (forecastRes.data && !forecastRes.data.error) {
                setForecast(forecastRes.data);
            }
            if (suggestionsRes.data?.suggestions?.length > 0) {
                setTopSuggestion(suggestionsRes.data.suggestions[0]);
            }
        }).finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div style={{ color: "#475569", padding: 40, fontFamily: "monospace" }}>
            Loading...
        </div>
    );

    return (
        <div style={{ padding: 32, fontFamily: "monospace" }}>
            <h2 style={{ color: "#f1f5f9", margin: "0 0 24px", fontSize: 20 }}>
                Dashboard
            </h2>

            {/* Top suggestion banner */}
            {topSuggestion && (
                <div style={{
                    background: `${SEVERITY_COLORS[topSuggestion.severity] || "#38bdf8"}0c`,
                    border: `1px solid ${SEVERITY_COLORS[topSuggestion.severity] || "#38bdf8"}40`,
                    borderLeft: `3px solid ${SEVERITY_COLORS[topSuggestion.severity] || "#38bdf8"}`,
                    borderRadius: 8, padding: "14px 20px", marginBottom: 24,
                    display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16,
                }}>
                    <div>
                        <div style={{ fontSize: 13, color: "#f1f5f9", fontWeight: 600, marginBottom: 4 }}>
                            {topSuggestion.title}
                        </div>
                        <div style={{ fontSize: 12, color: "#94a3b8" }}>
                            {topSuggestion.recommendation}
                        </div>
                    </div>
                    <Link to="/insights" style={{
                        fontSize: 11, color: SEVERITY_COLORS[topSuggestion.severity] || "#38bdf8",
                        textDecoration: "none", flexShrink: 0, whiteSpace: "nowrap",
                    }}>
                        View all →
                    </Link>
                </div>
            )}

            {/* Stat Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 16 }}>
                <StatCard
                    label="Total Spent"
                    value={formatCurrency(summary?.total_spent || 0)}
                    sub="All time"
                    color="#00ff9d"
                />
                <StatCard
                    label="Transactions"
                    value={summary?.total_transactions || 0}
                    sub="Total records"
                    color="#38bdf8"
                />
                <StatCard
                    label="Categories"
                    value={summary?.category_breakdown?.length || 0}
                    sub="Spending categories"
                    color="#a78bfa"
                />
            </div>

            {/* Forecast chart */}
            {forecast && forecast.predictions?.length > 0 ? (
                <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 24, marginBottom: 16 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 16 }}>
                        <div style={{ fontSize: 12, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                            30-Day Forecast
                        </div>
                        <div style={{ fontSize: 13, color: "#00ff9d" }}>
                            Predicted total: {formatCurrency(forecast.total_predicted)}
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={180}>
                        <AreaChart data={forecast.predictions}>
                            <defs>
                                <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#00ff9d" stopOpacity={0.3} />
                                    <stop offset="100%" stopColor="#00ff9d" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
                            <XAxis dataKey="date" tick={{ fill: "#475569", fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                            <YAxis tick={{ fill: "#475569", fontSize: 10 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                            <Tooltip
                                formatter={(val) => formatCurrency(val)}
                                contentStyle={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 6 }}
                                labelStyle={{ color: "#94a3b8" }}
                            />
                            <Area type="monotone" dataKey="predicted_amount" stroke="#00ff9d" fill="url(#forecastGradient)" strokeWidth={2} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            ) : (
                <div style={{
                    background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8,
                    padding: "40px 24px", marginBottom: 16, textAlign: "center",
                }}>
                    <div style={{ fontSize: 12, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>
                        30-Day Forecast
                    </div>
                    <div style={{ fontSize: 13, color: "#64748b" }}>
                        No forecast available yet. Add expenses and train the model to see predictions.
                    </div>
                </div>
            )}

            {/* Category Breakdown */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

                {/* Pie Chart */}
                <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 24 }}>
                    <div style={{ fontSize: 12, color: "#475569", marginBottom: 16, textTransform: "uppercase", letterSpacing: "0.1em" }}>
                        Spend by Category
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <PieChart>
                            <Pie
                                data={summary?.category_breakdown || []}
                                dataKey="total"
                                nameKey="category"
                                cx="50%" cy="50%"
                                outerRadius={80}
                            >
                                {summary?.category_breakdown?.map((entry) => (
                                    <Cell
                                        key={entry.category}
                                        fill={CATEGORY_COLORS[entry.category] || "#94a3b8"}
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(val) => formatCurrency(val)}
                                contentStyle={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 6 }}
                                labelStyle={{ color: "#94a3b8" }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Category Table */}
                <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 24 }}>
                    <div style={{ fontSize: 12, color: "#475569", marginBottom: 16, textTransform: "uppercase", letterSpacing: "0.1em" }}>
                        Category Breakdown
                    </div>
                    {summary?.category_breakdown?.map((cat) => (
                        <div key={cat.category} style={{
                            display: "flex", justifyContent: "space-between",
                            alignItems: "center", padding: "8px 0",
                            borderBottom: "1px solid #0f1923",
                        }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{
                                    width: 8, height: 8, borderRadius: "50%",
                                    background: CATEGORY_COLORS[cat.category] || "#94a3b8",
                                }} />
                                <span style={{ fontSize: 13, color: "#94a3b8" }}>{cat.category}</span>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div style={{ fontSize: 13, color: "#f1f5f9" }}>{formatCurrency(cat.total)}</div>
                                <div style={{ fontSize: 10, color: "#475569" }}>{cat.count} transactions</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}