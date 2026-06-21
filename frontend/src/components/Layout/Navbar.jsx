import { useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";

export default function Navbar() {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <div style={{
            background: "#0d1117", borderBottom: "1px solid #1e2d3d",
            padding: "0 32px", height: 56,
            display: "flex", alignItems: "center", justifyContent: "space-between",
        }}>
            <span style={{ color: "#00ff9d", fontFamily: "monospace", fontWeight: 700, fontSize: 16 }}>
                ExpenseTracker
            </span>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <span style={{ color: "#475569", fontFamily: "monospace", fontSize: 12 }}>
                    {user?.email}
                </span>
                <button onClick={handleLogout} style={{
                    background: "transparent", border: "1px solid #1e2d3d",
                    borderRadius: 5, color: "#64748b", padding: "5px 12px",
                    cursor: "pointer", fontFamily: "monospace", fontSize: 11,
                }}>
                    Logout
                </button>
            </div>
        </div>
    );
}