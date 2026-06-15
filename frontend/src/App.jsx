// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import useAuthStore from "./store/authStore";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ExpensesPage from "./pages/ExpensesPage";
import UploadPage from "./pages/UploadPage";
import InsightsPage from "./pages/InsightsPage";
import AnomaliesPage from "./pages/AnomaliesPage";
import Navbar from "./components/Layout/Navbar";
import Sidebar from "./components/Layout/Sidebar";
import RoadmapPage from "./pages/RoadmapPage";

// Protected route wrapper
function ProtectedLayout({ children }) {
    const token = useAuthStore((s) => s.token);
    if (!token) return <Navigate to="/login" replace />;
    return (
        <div style={{ background: "#07090d", minHeight: "100vh" }}>
            <Navbar />
            <div style={{ display: "flex" }}>
                <Sidebar />
                <div style={{ flex: 1 }}>{children}</div>
            </div>
        </div>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/dashboard" element={<ProtectedLayout><DashboardPage /></ProtectedLayout>} />
                <Route path="/expenses" element={<ProtectedLayout><ExpensesPage /></ProtectedLayout>} />
                <Route path="/upload" element={<ProtectedLayout><UploadPage /></ProtectedLayout>} />
                <Route path="/insights" element={<ProtectedLayout><InsightsPage /></ProtectedLayout>} />
                <Route path="/anomalies" element={<ProtectedLayout><AnomaliesPage /></ProtectedLayout>} />
                <Route path="/roadmap" element={<RoadmapPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
}