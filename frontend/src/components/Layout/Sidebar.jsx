// frontend/src/components/Layout/Sidebar.jsx
import { NavLink } from "react-router-dom";

const links = [
    { to: "/dashboard", label: "Dashboard", icon: "▦" },
    { to: "/expenses", label: "Expenses", icon: "≡" },
    { to: "/upload", label: "Upload CSV", icon: "↑" },
];

export default function Sidebar() {
    return (
        <div style={{
            width: 200, background: "#0d1117",
            borderRight: "1px solid #1e2d3d",
            padding: "24px 12px", minHeight: "calc(100vh - 56px)",
        }}>
            {links.map((link) => (
                <NavLink
                    key={link.to} to={link.to}
                    style={({ isActive }) => ({
                        display: "flex", alignItems: "center", gap: 10,
                        padding: "10px 14px", borderRadius: 6, marginBottom: 4,
                        fontFamily: "monospace", fontSize: 13, textDecoration: "none",
                        background: isActive ? "rgba(0,255,157,0.08)" : "transparent",
                        color: isActive ? "#00ff9d" : "#64748b",
                        border: isActive ? "1px solid rgba(0,255,157,0.2)" : "1px solid transparent",
                        transition: "all 0.15s",
                    })}
                >
                    <span>{link.icon}</span>
                    {link.label}
                </NavLink>
            ))}
        </div>
    );
}