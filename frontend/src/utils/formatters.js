// frontend/src/utils/formatters.js
export const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(amount);

export const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });

export const CATEGORY_COLORS = {
    Food: "#f97316",
    Transport: "#38bdf8",
    Shopping: "#a78bfa",
    Subscription: "#f43f5e",
    Utilities: "#facc15",
    Health: "#34d399",
    Entertainment: "#fb7185",
    Uncategorized: "#94a3b8",
    Other: "#94a3b8",
};

export const SEVERITY_COLORS = {
    high: "#f43f5e",
    medium: "#facc15",
    warning: "#facc15",
    low: "#38bdf8",
    info: "#38bdf8",
};