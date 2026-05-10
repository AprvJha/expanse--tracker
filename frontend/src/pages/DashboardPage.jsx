// frontend/src/pages/DashboardPage.jsx
import { useEffect, useState } from "react";
import { expensesAPI } from "../services/api";
import StatCard from "../components/UI/StatCard";
import { formatCurrency, CATEGORY_COLORS } from "../utils/formatters";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function DashboardPage() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        expensesAPI.summary()
            .then((res) => setSummary(res.data))
            .finally(() => setLoading(false));
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

            {/* Stat Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 32 }}>
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