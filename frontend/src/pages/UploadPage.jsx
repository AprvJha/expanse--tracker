// frontend/src/pages/UploadPage.jsx
import { useState, useRef } from "react";
import { uploadAPI } from "../services/api";

export default function UploadPage() {
    const [dragging, setDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const inputRef = useRef();

    const handleFile = (f) => {
        if (!f.name.endsWith(".csv")) {
            setError("Only CSV files accepted");
            return;
        }
        setFile(f);
        setResult(null);
        setError("");
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError("");
        try {
            const res = await uploadAPI.csv(file);
            setResult(res.data);
            setFile(null);
        } catch (err) {
            setError(err.response?.data?.detail || "Upload failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: 32, fontFamily: "monospace", maxWidth: 600 }}>
            <h2 style={{ color: "#f1f5f9", margin: "0 0 8px", fontSize: 20 }}>Upload CSV</h2>
            <p style={{ color: "#475569", fontSize: 13, margin: "0 0 32px" }}>
                Supports HDFC, SBI, Paytm, ICICI, and generic formats.
            </p>

            {/* Drop zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
                onClick={() => inputRef.current.click()}
                style={{
                    border: `2px dashed ${dragging ? "#00ff9d" : file ? "#38bdf8" : "#1e2d3d"}`,
                    borderRadius: 8, padding: "48px 24px", textAlign: "center",
                    cursor: "pointer", transition: "all 0.2s",
                    background: dragging ? "rgba(0,255,157,0.04)" : "transparent",
                    marginBottom: 20,
                }}
            >
                <input
                    ref={inputRef} type="file" accept=".csv"
                    style={{ display: "none" }}
                    onChange={(e) => handleFile(e.target.files[0])}
                />
                <div style={{ fontSize: 32, marginBottom: 12 }}>📂</div>
                {file ? (
                    <>
                        <div style={{ color: "#38bdf8", fontSize: 14, fontWeight: 600 }}>{file.name}</div>
                        <div style={{ color: "#475569", fontSize: 12, marginTop: 4 }}>
                            {(file.size / 1024).toFixed(1)} KB · Ready to upload
                        </div>
                    </>
                ) : (
                    <>
                        <div style={{ color: "#64748b", fontSize: 14 }}>Drop CSV here or click to browse</div>
                        <div style={{ color: "#334155", fontSize: 12, marginTop: 4 }}>HDFC · SBI · Paytm · ICICI · Generic</div>
                    </>
                )}
            </div>

            {error && (
                <div style={{
                    background: "#1a0a00", border: "1px solid #f43f5e40",
                    borderRadius: 6, padding: "10px 14px", marginBottom: 16,
                    color: "#f43f5e", fontSize: 13,
                }}>
                    {error}
                </div>
            )}

            {file && (
                <button
                    onClick={handleUpload} disabled={loading}
                    style={{
                        width: "100%", padding: 14, background: "#00ff9d",
                        border: "none", borderRadius: 6, color: "#07090d",
                        fontSize: 13, fontWeight: 700, cursor: "pointer",
                        fontFamily: "monospace",
                    }}
                >
                    {loading ? "Uploading..." : "Upload & Import"}
                </button>
            )}

            {/* Result */}
            {result && (
                <div style={{
                    marginTop: 24, background: "#0d1117",
                    border: "1px solid #00ff9d40", borderRadius: 8, padding: 24,
                }}>
                    <div style={{ color: "#00ff9d", fontWeight: 700, marginBottom: 16 }}>
                        ✓ Upload Successful
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        {[
                            { label: "Format Detected", value: result.format_detected?.toUpperCase() },
                            { label: "Rows Imported", value: result.inserted },
                            { label: "Original Rows", value: result.stats?.original_rows },
                            { label: "Duplicates Skipped", value: result.stats?.dropped_duplicates },
                            { label: "Nulls Removed", value: result.stats?.dropped_nulls },
                            { label: "Bad Dates Removed", value: result.stats?.dropped_bad_dates },
                        ].map((s) => (
                            <div key={s.label} style={{ background: "#060a0f", borderRadius: 6, padding: "10px 14px" }}>
                                <div style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 4 }}>
                                    {s.label}
                                </div>
                                <div style={{ fontSize: 16, color: "#f1f5f9", fontWeight: 600 }}>{s.value}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}