import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../services/api";

export default function RegisterPage() {
    const navigate = useNavigate();
    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await authAPI.register(form);
            navigate("/login");
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed");
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
                    Create Account
                </h1>
                <p style={{ color: "#475569", margin: "0 0 32px", fontSize: 13 }}>
                    Start tracking your expenses
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
                    {[
                        { key: "name", label: "Full Name", type: "text", placeholder: "John Doe" },
                        { key: "email", label: "Email", type: "email", placeholder: "you@gmail.com" },
                        { key: "password", label: "Password", type: "password", placeholder: "min 6 characters" },
                    ].map((field) => (
                        <div key={field.key} style={{ marginBottom: 16 }}>
                            <label style={{ display: "block", color: "#64748b", fontSize: 11, marginBottom: 6, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                                {field.label}
                            </label>
                            <input
                                type={field.type} required
                                value={form[field.key]}
                                onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                                placeholder={field.placeholder}
                                style={{
                                    width: "100%", padding: "10px 14px", background: "#060a0f",
                                    border: "1px solid #1e2d3d", borderRadius: 6, color: "#e2e8f0",
                                    fontSize: 13, fontFamily: "monospace", boxSizing: "border-box",
                                    outline: "none",
                                }}
                            />
                        </div>
                    ))}

                    <button
                        type="submit" disabled={loading}
                        style={{
                            width: "100%", padding: "12px", background: "#00ff9d",
                            border: "none", borderRadius: 6, color: "#07090d",
                            fontSize: 13, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                            fontFamily: "monospace", marginTop: 8,
                        }}
                    >
                        {loading ? "Creating account..." : "Create Account"}
                    </button>
                </form>

                <p style={{ color: "#475569", fontSize: 12, marginTop: 24, textAlign: "center" }}>
                    Already have an account?{" "}
                    <Link to="/login" style={{ color: "#00ff9d", textDecoration: "none" }}>
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}