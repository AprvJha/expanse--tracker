import { useEffect, useState } from "react";
import { expensesAPI } from "../services/api";
import { formatCurrency, formatDate, CATEGORY_COLORS } from "../utils/formatters";

const CATEGORIES = ["Food", "Transport", "Shopping", "Subscription", "Utilities", "Health", "Entertainment", "Other"];

export default function ExpensesPage() {
    const [expenses, setExpenses] = useState([]);
    const [pagination, setPagination] = useState({});
    const [page, setPage] = useState(1);
    const [category, setCategory] = useState("");
    const [loading, setLoading] = useState(true);

    const fetchExpenses = async () => {
        setLoading(true);
        try {
            const params = { page, limit: 20 };
            if (category) params.category = category;
            const res = await expensesAPI.list(params);
            setExpenses(res.data.data);
            setPagination(res.data.pagination);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchExpenses(); }, [page, category]);

    return (
        <div style={{ padding: 32, fontFamily: "monospace" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
                <h2 style={{ color: "#f1f5f9", margin: 0, fontSize: 20 }}>Expenses</h2>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ color: "#475569", fontSize: 12 }}>Filter:</span>
                    <select
                        value={category}
                        onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                        style={{
                            background: "#0d1117", border: "1px solid #1e2d3d",
                            borderRadius: 6, color: "#94a3b8", padding: "6px 12px",
                            fontSize: 12, fontFamily: "monospace", outline: "none",
                        }}
                    >
                        <option value="">All Categories</option>
                        {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
            </div>

            <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, overflow: "hidden" }}>
                <div style={{
                    display: "grid", gridTemplateColumns: "1fr 120px 140px 120px",
                    padding: "12px 20px", background: "#090d12",
                    borderBottom: "1px solid #1e2d3d",
                }}>
                    {["Merchant", "Category", "Date", "Amount"].map((h) => (
                        <span key={h} style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                            {h}
                        </span>
                    ))}
                </div>

                {loading ? (
                    <div style={{ padding: 40, textAlign: "center", color: "#475569" }}>Loading...</div>
                ) : expenses.map((exp) => (
                    <div key={exp.id} style={{
                        display: "grid", gridTemplateColumns: "1fr 120px 140px 120px",
                        padding: "12px 20px", borderBottom: "1px solid #0f1923",
                        transition: "background 0.1s",
                    }}
                        onMouseEnter={(e) => e.currentTarget.style.background = "#0d1520"}
                        onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                    >
                        <div>
                            <div style={{ fontSize: 13, color: "#e2e8f0" }}>{exp.merchant}</div>
                            {exp.is_anomaly && (
                                <span style={{ fontSize: 9, color: "#f43f5e", background: "#f43f5e18", border: "1px solid #f43f5e40", padding: "1px 6px", borderRadius: 3 }}>
                                    ANOMALY
                                </span>
                            )}
                        </div>
                        <div>
                            <span style={{
                                fontSize: 11, padding: "3px 8px", borderRadius: 4,
                                background: `${CATEGORY_COLORS[exp.category] || "#94a3b8"}18`,
                                color: CATEGORY_COLORS[exp.category] || "#94a3b8",
                                border: `1px solid ${CATEGORY_COLORS[exp.category] || "#94a3b8"}40`,
                            }}>
                                {exp.category}
                            </span>
                        </div>
                        <div style={{ fontSize: 12, color: "#64748b" }}>{formatDate(exp.date)}</div>
                        <div style={{ fontSize: 13, color: "#f1f5f9", fontWeight: 500 }}>{formatCurrency(exp.amount)}</div>
                    </div>
                ))}
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
                <span style={{ fontSize: 12, color: "#475569" }}>
                    {pagination.total} total · Page {pagination.page} of {pagination.pages}
                </span>
                <div style={{ display: "flex", gap: 8 }}>
                    <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        style={{
                            padding: "6px 14px", background: "transparent",
                            border: "1px solid #1e2d3d", borderRadius: 5,
                            color: page === 1 ? "#334155" : "#64748b",
                            cursor: page === 1 ? "not-allowed" : "pointer",
                            fontFamily: "monospace", fontSize: 12,
                        }}
                    >← Prev</button>
                    <button
                        onClick={() => setPage((p) => Math.min(pagination.pages, p + 1))}
                        disabled={page === pagination.pages}
                        style={{
                            padding: "6px 14px", background: "#00ff9d",
                            border: "none", borderRadius: 5,
                            color: "#07090d", cursor: page === pagination.pages ? "not-allowed" : "pointer",
                            fontFamily: "monospace", fontSize: 12, fontWeight: 700,
                        }}
                    >Next →</button>
                </div>
            </div>
        </div>
    );
}