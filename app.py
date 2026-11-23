import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Digital Biostatistics Academy | KSA", page_icon="📊", layout="wide")

@st.cache_data
def get_default_data():
    np.random.seed(42)
    h = np.arange(0, 24, 0.25)
    gluc = 125 + 35*np.exp(-((h-4.5)**2)/1.5) - 42*np.exp(-((h-16.5)**2)/3.0) + 75*np.exp(-((h-19.0)**2)/2.0)
    hr = 64 + 14*np.sin((h-9)*np.pi/12) + 12*np.exp(-((h-19.5)**2)/1.8)
    spo2 = np.clip(97.5 - 3.8*np.exp(-((h-3.0)**2)/2.5) + np.random.normal(0, 0.25, len(h)), 88, 99.5)
    hrv = np.clip(48 + 12*np.cos((h-3)*np.pi/12) - 16*np.exp(-((h-19.0)**2)/2.0), 15, 85)
    return pd.DataFrame({
        "Hour": h,
        "Glucose_mg_dL": np.round(gluc, 1),
        "Heart_Rate_bpm": np.round(hr, 1),
        "SpO2_pct": np.round(spo2, 1),
        "ECG_HRV_ms": np.round(hrv, 1)
    })

default_df = get_default_data()

st.title("📊 Digital Biostatistics Academy (DBA)")
st.caption("4-Device Virtual Care Ward Sandbox • Built for Saudi Vision 2030 Health Transformation")

# --- CSV UPLOAD & TEMPLATE BAR ---
with st.expander("📂 Data Ingestion: Use Saudi Virtual Ward Cohort or Upload Custom CSV", expanded=False):
    c1, c2, c3 = st.columns((1.2, 1.5, 1))
    mode = c1.radio("Telemetry Source:", ("Built-in Saudi Patient (SA-1042)", "Upload Custom CSV"))
    up_file = c2.file_uploader("Upload CSV (Hour, Glucose_mg_dL, Heart_Rate_bpm, SpO2_pct, ECG_HRV_ms)", type=("csv",))
    c3.download_button("⬇️ Download Sample CSV", default_df.to_csv(index=False).encode("utf-8"), "saudi_telemetry.csv", "text/csv")

if mode == "Upload Custom CSV" and up_file is not None:
    df = pd.read_csv(up_file).sort_values("Hour").reset_index(drop=True)
    st.success(f"✅ Loaded {len(df)} telemetry points from `{up_file.name}`!")
else:
    df = default_df.copy()

st.info("👤 **Patient ID: SA-1042** (Riyadh Virtual Care Ward) | **4 Active Streams:** `1. CGM Glucose` • `2. Smartwatch HR` • `3. Wireless Pulse Oximeter (SpO₂)` • `4. Continuous ECG Patch (HRV)`")

# --- DEVICE & INTERVENTION CONTROLS ---
ctrl1, ctrl2, ctrl3 = st.columns((1.3, 1.2, 1.2))
device_view = ctrl1.selectbox(
    "Select Connected Medical Device Module:",
    (
        "All 4 Devices — Unified Multimodal Fusion",
        "Device 1: Continuous Glucose Monitor (CGM)",
        "Device 2: Smartwatch Heart Rate (Circadian)",
        "Device 3: Wireless Pulse Oximeter (SpO₂)",
        "Device 4: Continuous ECG Patch (HRV Stress)"
    )
)
show_band = ctrl2.toggle("Show 95% Functional Confidence Band (FDA)", value=True)
nudge_on = ctrl3.toggle("🚀 Simulate 16:00 Virtual Ward Intervention", value=False)

# Apply simulated clinical intervention if toggled ON
g_vals = df["Glucose_mg_dL"].copy()
hrv_vals = df["ECG_HRV_ms"].copy()
if nudge_on:
    g_vals = g_vals + 22*np.exp(-((df["Hour"]-16.5)**2)/3.0) - 35*np.exp(-((df["Hour"]-19.0)**2)/2.0)
    hrv_vals = hrv_vals + 12*np.exp(-((df["Hour"]-19.0)**2)/2.5)

# --- 4 LIVE KPI CARDS (ONE FOR EACH DEVICE) ---
k1, k2, k3, k4 = st.columns(4)
tir = int(np.mean((g_vals >= 70) & (g_vals <= 180)) * 100)
k1.metric("1. CGM Time-in-Range", f"{tir}%", f"Mean: {np.mean(g_vals):.0f} mg/dL")
k2.metric("2. Smartwatch Peak HR", f"{np.max(df['Heart_Rate_bpm']):.0f} bpm", f"Mean: {np.mean(df['Heart_Rate_bpm']):.0f} bpm")
k3.metric("3. Oximeter Nadir SpO₂", f"{np.min(df['SpO2_pct']):.1f}%", "Nocturnal dip at 03:00")
k4.metric("4. ECG Patch Mean HRV", f"{np.mean(hrv_vals):.0f} ms", "+Autonomic Stability" if nudge_on else "Post-Iftar dip")

# --- INTERACTIVE FUNCTIONAL CHART ---
fig = go.Figure()

def add_stream(y_series, name, color, dash="solid"):
    fig.add_trace(go.Scatter(x=df["Hour"], y=y_series, mode="lines", name=name, line=dict(color=color, width=3, dash=dash)))
    if show_band:
        std = y_series.rolling(4, min_periods=1).std().fillna(y_series.std()*0.15)
        fig.add_trace(go.Scatter(
            x=pd.concat((df["Hour"], df["Hour"].iloc[::-1])),
            y=pd.concat((y_series + 1.5*std, (y_series - 1.5*std).iloc[::-1])),
            fill="toself", fillcolor="rgba(0,128,128,0.10)", line=dict(width=0), showlegend=False
        ))

if "All 4 Devices" in device_view:
    add_stream(g_vals, "1. CGM Glucose (mg/dL)", "#008080")
    add_stream(df["Heart_Rate_bpm"], "2. Smartwatch HR (bpm)", "#dc3545", "dot")
    add_stream(df["SpO2_pct"], "3. Pulse Oximeter SpO₂ (%)", "#0d6efd")
    add_stream(hrv_vals, "4. ECG Patch HRV (ms)", "#fd7e14")
elif "Device 1" in device_view:
    fig.add_hrect(y0=70, y1=180, fillcolor="green", opacity=0.08, line_width=0)
    add_stream(g_vals, "1. CGM Glucose (mg/dL)", "#008080")
elif "Device 2" in device_view:
    add_stream(df["Heart_Rate_bpm"], "2. Smartwatch Heart Rate (bpm)", "#dc3545")
elif "Device 3" in device_view:
    fig.add_hline(y=94, line_dash="dash", line_color="red", annotation_text="Hypoxia Alert (94%)")
    add_stream(df["SpO2_pct"], "3. Wireless Pulse Oximeter SpO₂ (%)", "#0d6efd")
else:
    add_stream(hrv_vals, "4. Continuous ECG Patch HRV (ms)", "#fd7e14")

fig.update_layout(title=f"Live Functional Trajectory — {device_view}", xaxis_title="Hour of Day (00:00 - 24:00)", yaxis_title="Telemetry Value", height=380, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- COMPETENCY MICRO-CREDENTIAL ---
st.divider()
st.subheader("🎓 Clinician Micro-Credential & AI Copilot")
q1, q2 = st.columns(2)
with q1:
    ans = st.radio(
        "Why must Virtual Care Ward clinicians model all 4 devices jointly?",
        (
            "Single-device averages miss cross-system interactions (e.g., nocturnal SpO₂ drops + post-meal glucose surges triggering ECG HRV stress).",
            "Wireless devices only record data once a week."
        )
    )
    if st.button("Verify & Claim SCFHS-Aligned CPD Credit"):
        if "cross-system" in ans:
            st.success("✅ Verified! You earned 2.5 Multimodal Digital Biostatistics CPD Credits.")
            st.balloons()
        else:
            st.error("Try the first option!")
q2.info("**AI Biostatistics Copilot:**\n\n*Use the dropdown above to inspect each of the 4 medical devices individually or view all 4 streams fused together.*")
