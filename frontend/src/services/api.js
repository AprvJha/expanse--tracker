// frontend/src/services/api.js
import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: { "Content-Type": "application/json" },
});

// Attach token to every request automatically
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auto logout on 401
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

// ── Auth ──────────────────────────────────────────────
export const authAPI = {
    register: (data) => api.post("/auth/register", data),
    login: (data) => api.post("/auth/login", data),
    me: () => api.get("/auth/me"),
};

// ── Expenses ──────────────────────────────────────────
export const expensesAPI = {
    list: (params) => api.get("/expenses/", { params }),
    summary: () => api.get("/expenses/summary"),
    create: (data) => api.post("/expenses/", data),
    update: (id, data) => api.put(`/expenses/${id}`, data),
    delete: (id) => api.delete(`/expenses/${id}`),
};

// ── Upload ────────────────────────────────────────────
export const uploadAPI = {
    csv: (file) => {
        const formData = new FormData();
        formData.append("file", file);
        return api.post("/upload/csv", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
    },
};

export default api;