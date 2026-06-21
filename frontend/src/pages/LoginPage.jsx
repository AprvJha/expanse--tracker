import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../services/api";
import useAuthStore from "../store/authStore";

export default function LoginPage() {
    const navigate = useNavigate();
    const login = useAuthStore((s) => s.login);
    const [form, setForm] = useState({ email: "", password: "" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const res = await authAPI.login(form);
            login(res.data.access_token, res.data.user);
            navigate("/dashboard");
        } catch (err) {
            setError(err.response?.data?.detail || "Login failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: "100vh", background: "#07090d",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "monospace",
        }}>
            <div style={{
                background: "#0d1117", border: "1px solid #1e2d3d",
                borderRadius: 8, padding: 40, width: "100%", maxWidth: 400,
            }}>
                <h1 style={{ color: "#00ff9d", margin: "0 0 8px", fontSize: 24 }}>
                    Expense Tracker
                </h1>
                <p style={{ color: "#475569", margin: "0 0 32px", fontSize: 13 }}>
                    Sign in to your account
                </p>

                {error && (
                    <div style={{
                        background: "#1a0a00", border: "1px solid #f43f5e40",
                        borderRadius: 6, padding: "10px 14px", marginBottom: 20,
                        color: "#f43f5e", fontSize: 13,
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 16 }}>
                        <label style={{ display: "block", color: "#64748b", fontSize: 11, marginBottom: 6, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                            Email
                        </label>
                        <input
                            type="email" required
                            value={form.email}
                            onChange={(e) => setForm({ ...form, email: e.target.value })}
                            style={{
                                width: "100%", padding: "10px 14px", background: "#060a0f",
                                border: "1px solid #1e2d3d", borderRadius: 6, color: "#e2e8f0",
                                fontSize: 13, fontFamily: "monospace", boxSizing: "border-box",
                                outline: "none",
                            }}
                            placeholder="you@gmail.com"
                        />
                    </div>

                    <div style={{ marginBottom: 24 }}>
                        <label style={{ display: "block", color: "#64748b", fontSize: 11, marginBottom: 6, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                            Password
                        </label>
                        <input
                            type="password" required
                            value={form.password}
                            onChange={(e) => setForm({ ...form, password: e.target.value })}
                            style={{
                                width: "100%", padding: "10px 14px", background: "#060a0f",
                                border: "1px solid #1e2d3d", borderRadius: 6, color: "#e2e8f0",
                                fontSize: 13, fontFamily: "monospace", boxSizing: "border-box",
                                outline: "none",
                            }}
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit" disabled={loading}
                        style={{
                            width: "100%", padding: "12px", background: "#00ff9d",
                            border: "none", borderRadius: 6, color: "#07090d",
                            fontSize: 13, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                            fontFamily: "monospace", letterSpacing: "0.05em",
                        }}
                    >
                        {loading ? "Signing in..." : "Sign In"}
                    </button>
                </form>

                <p style={{ color: "#475569", fontSize: 12, marginTop: 24, textAlign: "center" }}>
                    No account?{" "}
                    <Link to="/register" style={{ color: "#00ff9d", textDecoration: "none" }}>
                        Register here
                    </Link>
                </p>
            </div>
        </div>
    );
}