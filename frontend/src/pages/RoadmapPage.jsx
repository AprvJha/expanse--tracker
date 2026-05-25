import { useState } from "react";

const phases = [
  {
    id: 1,
    label: "Phase 1",
    title: "Foundation & Data Layer",
    duration: "Week 1–2",
    tag: "CORE",
    tagColor: "#00ff9d",
    accent: "#00ff9d",
    description: "Build the backbone. No ML yet. Get the plumbing right.",
    architecture: [
      { layer: "Frontend", tech: "React + Vite", note: "Component architecture, routing" },
      { layer: "Backend", tech: "FastAPI (Python)", note: "REST endpoints, data validation" },
      { layer: "Database", tech: "MongoDB Atlas", note: "Flexible schema for transactions" },
      { layer: "Auth", tech: "JWT + bcrypt", note: "Secure user sessions" },
    ],
    deliverables: [
      { item: "CSV Upload & Parser", detail: "Handle messy bank statement formats (Paytm, HDFC, SBI)" },
      { item: "Manual Expense Entry", detail: "CRUD with amount, date, category, notes" },
      { item: "Data Cleaning Pipeline", detail: "Strip duplicates, normalize date formats, handle nulls" },
      { item: "Realistic Sample Data Generator", detail: "1,000+ transactions, realistic patterns, seasonal spikes" },
      { item: "Basic Dashboard Shell", detail: "Skeleton UI — don't polish yet, just structure" },
    ],
    interview_angle: "\"I started with data quality because ML is only as good as its input. I built a parser that handles 5 different bank CSV formats.\"",
    resume_line: "Built multi-format bank statement parser with automated data cleaning pipeline",
    warning: "Don't touch ML in this phase. Clean data first.",
  },
  {
    id: 2,
    label: "Phase 2",
    title: "Smart Categorization Engine",
    duration: "Week 3",
    tag: "ML",
    tagColor: "#ff6b35",
    accent: "#ff6b35",
    description: "Two-tier approach: rule-based baseline → ML upgrade. Show the delta.",
    architecture: [
      { layer: "Tier 1", tech: "Keyword Mapping", note: "Regex + dictionary lookup (baseline)" },
      { layer: "Tier 2", tech: "TF-IDF + Logistic Regression", note: "sklearn, trained on merchant names" },
      { layer: "Evaluation", tech: "Accuracy / F1 Score", note: "Side-by-side comparison table" },
      { layer: "API", tech: "FastAPI ML endpoint", note: "POST /categorize → {category, confidence}" },
    ],
    deliverables: [
      { item: "Rule-Based Classifier", detail: "Keywords: 'swiggy' → Food, 'uber' → Transport, 'netflix' → Subscription" },
      { item: "TF-IDF + Logistic Regression Model", detail: "Trained on merchant name + description fields" },
      { item: "Model Evaluation Dashboard", detail: "Accuracy %, confusion matrix, per-category F1" },
      { item: "Comparison Table", detail: "Rule-based: 73% accuracy → ML: 89% accuracy — THIS is the story" },
      { item: "Retraining on User Corrections", detail: "User fixes a category → feeds back into model" },
    ],
    interview_angle: "\"I didn't just use ML — I proved it was better than the baseline. Rule-based got 73%, logistic regression got 89% on held-out test data.\"",
    resume_line: "Implemented 2-tier categorization: keyword baseline vs TF-IDF + Logistic Regression (73% → 89% accuracy improvement)",
    warning: "Don't skip the baseline. The comparison IS the impressive part.",
  },
  {
    id: 3,
    label: "Phase 3",
    title: "Behavioral Insights Engine",
    duration: "Week 4",
    tag: "ANALYTICS",
    tagColor: "#a78bfa",
    accent: "#a78bfa",
    description: "This is data science. Not charts. Patterns that mean something.",
    architecture: [
      { layer: "Engine", tech: "Pandas + NumPy", note: "Time-series aggregation, rolling windows" },
      { layer: "Patterns", tech: "Weekday vs Weekend", note: "Behavioral segmentation" },
      { layer: "Stats", tech: "Concentration Analysis", note: "Top-N category share" },
      { layer: "Output", tech: "Insight Cards API", note: "GET /insights → [{type, message, severity}]" },
    ],
    deliverables: [
      { item: "Weekend vs Weekday Spending Ratio", detail: "\"Weekend spending is 1.8× weekday average\"" },
      { item: "Category Concentration Insight", detail: "\"Top 3 categories = 72% of your expenses\"" },
      { item: "Recurring Expense Detection", detail: "Flag subscriptions by regularity + amount similarity" },
      { item: "Monthly Trend Narrative", detail: "\"August was your highest spend month in 6 months\"" },
      { item: "Merchant Frequency Analysis", detail: "\"You visited Swiggy 23 times this month (+40% vs last)\"" },
    ],
    interview_angle: "\"Anyone can make charts. I generate behavioral narratives — weekend patterns, concentration analysis, merchant frequency spikes.\"",
    resume_line: "Designed behavioral analytics engine detecting spending patterns: temporal segmentation, concentration metrics, recurring cost detection",
    warning: "Each insight must have a formula behind it. Not vibes.",
  },
  {
    id: 4,
    label: "Phase 4",
    title: "Anomaly Detection System",
    duration: "Week 5",
    tag: "STRONGEST",
    tagColor: "#f43f5e",
    accent: "#f43f5e",
    description: "Your differentiator. Most projects skip this. Don't.",
    architecture: [
      { layer: "Level 1", tech: "Z-Score Detection", note: "Per-category statistical baseline" },
      { layer: "Level 2", tech: "Isolation Forest", note: "sklearn, unsupervised, handles non-normal data" },
      { layer: "Alerts", tech: "Alert API", note: "POST /alerts → severity: low/medium/high" },
      { layer: "Viz", tech: "Scatter overlay on chart", note: "Red dots on anomaly points" },
    ],
    deliverables: [
      { item: "Z-Score Anomaly Detector", detail: "Flag if transaction > mean + 2σ within category" },
      { item: "Isolation Forest Model", detail: "Multivariate: amount + category + time-of-day features" },
      { item: "Alert System", detail: "\"Unusual: ₹1,200 Food spend (3.1σ above your norm)\"" },
      { item: "Anomaly Visualization", detail: "Red highlighted points on time-series chart" },
      { item: "False Positive Control", detail: "Suppress alerts for known recurring amounts" },
      { item: "Precision Metric", detail: "Track alert precision on labeled test data" },
    ],
    interview_angle: "\"I implemented two-tier anomaly detection — Z-score for interpretability, Isolation Forest for accuracy. I measured precision on labeled test transactions.\"",
    resume_line: "Built dual-method anomaly detection (Z-score + Isolation Forest) with real-time alerting and per-category statistical baselines",
    warning: "Label at least 50 test anomalies manually. Measure precision. Show the number.",
  },
  {
    id: 5,
    label: "Phase 5",
    title: "Expense Prediction",
    duration: "Week 6",
    tag: "ML",
    tagColor: "#ff6b35",
    accent: "#38bdf8",
    description: "Keep it honest. Simple + explainable beats Prophet you can't explain.",
    architecture: [
      { layer: "Baseline", tech: "Linear Regression", note: "Date index → total spend" },
      { layer: "Improved", tech: "Rolling Average", note: "7-day, 30-day smoothing" },
      { layer: "Features", tech: "Weekend flag, category", note: "Categorical encoding" },
      { layer: "Metric", tech: "MAE + RMSE", note: "Reported on 20% holdout" },
    ],
    deliverables: [
      { item: "Linear Regression Forecaster", detail: "Next 7-day and 30-day spend prediction" },
      { item: "Rolling Average Baseline", detail: "Compare against naive rolling mean" },
      { item: "Seasonality Features", detail: "Weekend flag, day-of-month, payday detection" },
      { item: "MAE Comparison Table", detail: "Linear vs Rolling — show which wins and why" },
      { item: "Prediction UI", detail: "\"Predicted spend this month: ₹14,200 (±₹800)\"" },
    ],
    interview_angle: "\"I chose Linear Regression over Prophet because I can explain every coefficient. MAE on holdout was ₹420 against a ₹12,000 average — 3.5% error.\"",
    resume_line: "Developed expense forecasting model (Linear Regression + rolling features), achieving 3.5% MAE on 20% holdout set",
    warning: "If asked about Prophet in interview — only use it if you can explain additive seasonality. Otherwise stick to Linear.",
  },
  {
    id: 6,
    label: "Phase 6",
    title: "Smart Suggestions & Rules Engine",
    duration: "Week 7",
    tag: "PRODUCT",
    tagColor: "#facc15",
    accent: "#facc15",
    description: "Honest rule-based logic beats fake AI. Be precise.",
    architecture: [
      { layer: "Engine", tech: "Python Rules + Thresholds", note: "Data-driven, not hardcoded" },
      { layer: "Triggers", tech: "Category % thresholds", note: "Configurable per user" },
      { layer: "Output", tech: "Suggestion cards", note: "Priority: high / medium / low" },
      { layer: "UI", tech: "Dismissible alerts", note: "Track which suggestions were acted on" },
    ],
    deliverables: [
      { item: "Category Threshold Alerts", detail: "Food > 30% → trigger reduction suggestion" },
      { item: "Subscription Audit", detail: "List all recurring charges, flag unused ones" },
      { item: "Savings Opportunity Calculator", detail: "\"Reducing dining by 20% saves ₹2,400/month\"" },
      { item: "Peer Comparison (Simulated)", detail: "\"You spend 40% more on transport than similar profiles\"" },
      { item: "Suggestion Effectiveness Tracking", detail: "Did user spending change after suggestion?" },
    ],
    interview_angle: "\"I was explicit: these are rule-based suggestions, not 'AI'. I derived thresholds from the data — median category splits across all users.\"",
    resume_line: "Designed data-driven financial suggestions engine with category thresholds derived from user spending distributions",
    warning: "Never say 'AI-powered' for this. Say 'data-driven rule engine'. Honesty impresses more.",
  },
  {
    id: 7,
    label: "Phase 7",
    title: "Deployment & System Design",
    duration: "Week 8",
    tag: "NON-NEGOTIABLE",
    tagColor: "#00ff9d",
    accent: "#00ff9d",
    description: "Undeployed projects are invisible. Deploy everything, document the architecture.",
    architecture: [
      { layer: "Frontend", tech: "Vercel", note: "Auto CI/CD from GitHub main branch" },
      { layer: "Backend", tech: "Render / Railway", note: "FastAPI containerized" },
      { layer: "ML Service", tech: "Separate FastAPI on Render", note: "Isolated — can scale independently" },
      { layer: "Database", tech: "MongoDB Atlas M0", note: "Free tier, IP whitelist" },
    ],
    deliverables: [
      { item: "3-Service Architecture Live", detail: "Frontend + Backend + ML API all deployed and connected" },
      { item: "Environment Config", detail: ".env management, secrets out of GitHub" },
      { item: "Architecture Diagram", detail: "Draw.io / Excalidraw — service boxes, data flow arrows" },
      { item: "README with Setup Guide", detail: "Recruiter should be able to run locally in 3 commands" },
      { item: "Model Metrics Dashboard", detail: "Live page showing: categorization accuracy, MAE, anomaly precision" },
      { item: "Demo Video (3 min)", detail: "Walk through: upload CSV → insights → anomaly alert → prediction" },
    ],
    interview_angle: "\"I separated the ML service because categorization and anomaly models update on different cycles. Frontend deployment is decoupled from model retraining.\"",
    resume_line: "Deployed 3-service architecture (React/Vercel + FastAPI/Render + ML API) with MongoDB Atlas and automated CI/CD",
    warning: "The architecture diagram alone will get you asked about system design in interviews.",
  },
];

const metrics = [
  { label: "Categorization Accuracy", target: ">85%", tool: "sklearn classification_report" },
  { label: "Prediction MAE", target: "<5% of avg spend", tool: "sklearn mean_absolute_error" },
  { label: "Anomaly Precision", target: ">80%", tool: "Manually labeled test set" },
  { label: "Data Coverage", target: "1,000+ transactions", tool: "Sample data generator" },
];

const stack = [
  { area: "Frontend", tech: "React + Vite + Recharts" },
  { area: "Backend", tech: "FastAPI + Pydantic" },
  { area: "ML", tech: "scikit-learn + Pandas + NumPy" },
  { area: "Database", tech: "MongoDB Atlas" },
  { area: "Auth", tech: "JWT + bcrypt" },
  { area: "Deploy", tech: "Vercel + Render + Railway" },
];

export default function Roadmap() {
  const [activePhase, setActivePhase] = useState(null);
  const [activeTab, setActiveTab] = useState("deliverables");

  const selected = phases.find(p => p.id === activePhase);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#080c10",
      color: "#e2e8f0",
      fontFamily: "'DM Mono', 'Courier New', monospace",
      padding: "0",
    }}>
      {/* Scan line overlay */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
        backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,157,0.015) 2px, rgba(0,255,157,0.015) 4px)",
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 1100, margin: "0 auto", padding: "40px 24px" }}>

        {/* Header */}
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
            <div style={{ width: 8, height: 8, background: "#00ff9d", borderRadius: "50%", boxShadow: "0 0 8px #00ff9d" }} />
            <span style={{ fontSize: 11, letterSpacing: "0.2em", color: "#00ff9d", textTransform: "uppercase" }}>Project Roadmap</span>
          </div>
          <h1 style={{
            fontSize: "clamp(28px, 5vw, 52px)", fontWeight: 700, margin: "0 0 8px",
            fontFamily: "'DM Mono', monospace", letterSpacing: "-0.02em",
            background: "linear-gradient(135deg, #fff 60%, #00ff9d)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>
            Smart Expense Tracker
          </h1>
          <p style={{ color: "#64748b", fontSize: 14, margin: 0, letterSpacing: "0.05em" }}>
            8-WEEK BUILD PLAN · INDUSTRIAL GRADE · RESUME READY
          </p>
        </div>

        {/* Stack + Metrics row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 40 }}>
          <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 20 }}>
            <div style={{ fontSize: 10, letterSpacing: "0.15em", color: "#475569", marginBottom: 14, textTransform: "uppercase" }}>Tech Stack</div>
            {stack.map(s => (
              <div key={s.area} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: "1px solid #0f1923" }}>
                <span style={{ fontSize: 11, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>{s.area}</span>
                <span style={{ fontSize: 12, color: "#94a3b8" }}>{s.tech}</span>
              </div>
            ))}
          </div>
          <div style={{ background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8, padding: 20 }}>
            <div style={{ fontSize: 10, letterSpacing: "0.15em", color: "#475569", marginBottom: 14, textTransform: "uppercase" }}>Success Metrics</div>
            {metrics.map(m => (
              <div key={m.label} style={{ marginBottom: 12 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                  <span style={{ fontSize: 11, color: "#94a3b8" }}>{m.label}</span>
                  <span style={{ fontSize: 11, color: "#00ff9d", fontWeight: 600 }}>{m.target}</span>
                </div>
                <div style={{ fontSize: 10, color: "#334155" }}>{m.tool}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Phase Timeline */}
        <div style={{ fontSize: 10, letterSpacing: "0.15em", color: "#475569", marginBottom: 16, textTransform: "uppercase" }}>
          Click a phase to expand
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4, marginBottom: 40 }}>
          {phases.map((phase) => {
            const isOpen = activePhase === phase.id;
            return (
              <div key={phase.id}
                onClick={() => setActivePhase(isOpen ? null : phase.id)}
                style={{
                  background: isOpen ? "#0d1117" : "#090d12",
                  border: `1px solid ${isOpen ? phase.accent : "#1a2332"}`,
                  borderRadius: 6,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  overflow: "hidden",
                  boxShadow: isOpen ? `0 0 20px ${phase.accent}18` : "none",
                }}
              >
                {/* Phase Header Row */}
                <div style={{ display: "flex", alignItems: "center", padding: "16px 20px", gap: 16 }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: 4, border: `1px solid ${phase.accent}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 11, color: phase.accent, fontWeight: 700, flexShrink: 0,
                    boxShadow: isOpen ? `0 0 10px ${phase.accent}40` : "none",
                  }}>
                    {phase.id}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: isOpen ? "#f1f5f9" : "#94a3b8" }}>
                        {phase.title}
                      </span>
                      <span style={{
                        fontSize: 9, letterSpacing: "0.12em", padding: "2px 8px",
                        background: `${phase.tagColor}18`, color: phase.tagColor,
                        border: `1px solid ${phase.tagColor}40`, borderRadius: 3,
                        textTransform: "uppercase",
                      }}>
                        {phase.tag}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: 11, color: "#334155", flexShrink: 0 }}>{phase.duration}</div>
                  <div style={{ color: "#334155", fontSize: 14, transform: isOpen ? "rotate(180deg)" : "none", transition: "0.2s" }}>▾</div>
                </div>

                {/* Expanded Content */}
                {isOpen && (
                  <div style={{ padding: "0 20px 20px" }}>
                    <p style={{ fontSize: 13, color: "#64748b", margin: "0 0 20px", paddingTop: 0 }}>{phase.description}</p>

                    {/* Architecture Table */}
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#334155", marginBottom: 10, textTransform: "uppercase" }}>Architecture</div>
                      <div style={{ background: "#060a0f", border: "1px solid #1a2332", borderRadius: 6, overflow: "hidden" }}>
                        {phase.architecture.map((a, i) => (
                          <div key={i} style={{
                            display: "grid", gridTemplateColumns: "100px 180px 1fr",
                            padding: "10px 14px", gap: 16,
                            borderBottom: i < phase.architecture.length - 1 ? "1px solid #0f1923" : "none",
                            alignItems: "center",
                          }}>
                            <span style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: "0.08em" }}>{a.layer}</span>
                            <span style={{ fontSize: 12, color: phase.accent, fontWeight: 500 }}>{a.tech}</span>
                            <span style={{ fontSize: 11, color: "#475569" }}>{a.note}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Tabs */}
                    <div style={{ display: "flex", gap: 4, marginBottom: 14 }}>
                      {["deliverables", "interview", "resume"].map(tab => (
                        <button key={tab} onClick={(e) => { e.stopPropagation(); setActiveTab(tab); }} style={{
                          padding: "5px 14px", fontSize: 10, letterSpacing: "0.1em",
                          textTransform: "uppercase", borderRadius: 4, cursor: "pointer",
                          background: activeTab === tab ? phase.accent : "transparent",
                          color: activeTab === tab ? "#080c10" : "#475569",
                          border: `1px solid ${activeTab === tab ? phase.accent : "#1a2332"}`,
                          fontFamily: "inherit", fontWeight: activeTab === tab ? 700 : 400,
                          transition: "all 0.15s",
                        }}>
                          {tab}
                        </button>
                      ))}
                    </div>

                    {activeTab === "deliverables" && (
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {phase.deliverables.map((d, i) => (
                          <div key={i} style={{
                            display: "flex", gap: 14, padding: "10px 14px",
                            background: "#060a0f", borderRadius: 5, border: "1px solid #0f1923",
                            alignItems: "flex-start",
                          }}>
                            <div style={{ width: 6, height: 6, background: phase.accent, borderRadius: "50%", flexShrink: 0, marginTop: 5, boxShadow: `0 0 5px ${phase.accent}` }} />
                            <div>
                              <div style={{ fontSize: 12, color: "#cbd5e1", fontWeight: 500, marginBottom: 2 }}>{d.item}</div>
                              <div style={{ fontSize: 11, color: "#475569" }}>{d.detail}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeTab === "interview" && (
                      <div style={{
                        padding: 16, background: "#060a0f", borderRadius: 6,
                        border: `1px solid ${phase.accent}30`,
                        borderLeft: `3px solid ${phase.accent}`,
                      }}>
                        <div style={{ fontSize: 10, letterSpacing: "0.1em", color: phase.accent, marginBottom: 10, textTransform: "uppercase" }}>How to explain this in interviews</div>
                        <p style={{ fontSize: 13, color: "#94a3b8", margin: 0, lineHeight: 1.7, fontStyle: "italic" }}>{phase.interview_angle}</p>
                      </div>
                    )}

                    {activeTab === "resume" && (
                      <div>
                        <div style={{
                          padding: 16, background: "#060a0f", borderRadius: 6,
                          border: "1px solid #1a2332", marginBottom: 12,
                        }}>
                          <div style={{ fontSize: 10, letterSpacing: "0.1em", color: "#475569", marginBottom: 10, textTransform: "uppercase" }}>Resume Bullet</div>
                          <p style={{ fontSize: 13, color: "#e2e8f0", margin: 0, lineHeight: 1.7 }}>• {phase.resume_line}</p>
                        </div>
                        {phase.warning && (
                          <div style={{
                            padding: 12, background: "#1a0a00", borderRadius: 6,
                            border: "1px solid #f43f5e40", display: "flex", gap: 10, alignItems: "flex-start",
                          }}>
                            <span style={{ color: "#f43f5e", fontSize: 14, flexShrink: 0 }}>⚠</span>
                            <span style={{ fontSize: 12, color: "#94a3b8" }}>{phase.warning}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Summary footer */}
        <div style={{
          background: "#0d1117", border: "1px solid #1e2d3d", borderRadius: 8,
          padding: "20px 24px", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20,
        }}>
          {[
            { label: "Total Duration", value: "8 Weeks" },
            { label: "ML Models", value: "4 Models" },
            { label: "Deployments", value: "3 Services" },
            { label: "Metrics Tracked", value: "3 KPIs" },
          ].map(s => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#00ff9d", marginBottom: 4 }}>{s.value}</div>
              <div style={{ fontSize: 10, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
