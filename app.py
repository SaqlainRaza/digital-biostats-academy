import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Digital Biostatistics Academy | KSA",
    page_icon="📊",
    layout="wide"
)

# --- BUILT-IN SYNTHETIC SAUDI VIRTUAL WARD DATA ---
@st.cache_data
def generate_patient_multimodal_data():
    np.random.seed(42)
    hours = np.arange(0, 24, 0.25)

    # Device 1: CGM Glucose (mg/dL)
    std_gluc = 135 + 25 * np.sin((hours - 8) * np.pi / 12) + 15 * np.exp(-((hours - 14) ** 2) / 2)
    ramadan_gluc = (
        125
        + 35 * np.exp(-((hours - 4.5) ** 2) / 1.5)
        - 42 * np.exp(-((hours - 16.5) ** 2) / 3.0)
        + 75 * np.exp(-((hours - 19.0) ** 2) / 2.0)
    )

    # Device 2: Smartwatch Heart Rate (bpm)
    hr_curve = 64 + 14 * np.sin((hours - 9) * np.pi / 12) + 12 * np.exp(-((hours - 19.5) ** 2) / 1.8)
    hr_upper = hr_curve + np.random.uniform(4, 7, size=len(hours))
    hr_lower = hr_curve - np.random.uniform(4, 7, size=len(hours))

    # Device 3: Wireless Pulse Oximeter (SpO2 %)
    spo2_curve = 97.5 - 3.8 * np.exp(-((hours - 3.0) ** 2) / 2.5) + np.random.normal(0, 0.3, len(hours))
    spo2_curve = np.clip(spo2_curve, 88.0, 99.5)

    # Device 4: Continuous ECG Patch HRV (ms)
    hrv_curve = 48 + 12 * np.cos((hours - 3) * np.pi / 12) - 16 * np.exp(-((hours - 19.0) ** 2) / 2.0)
    hrv_curve = np.clip(hrv_curve, 15.0, 85.0)

    return pd.DataFrame({
        "Hour": hours,
        "Standard_Mean": np.round(std_gluc, 1),
        "Standard_Upper": np.round(std_gluc + 15, 1),
        "Standard_Lower": np.round(std_gluc - 15, 1),
        "Ramadan_Mean": np.round(ramadan_gluc, 1),
        "Ramadan_Upper": np.round(ramadan_gluc + 18, 1),
        "Ramadan_Lower": np.round(ramadan_gluc - 18, 1),
        "HR_Mean": np.round(hr_curve, 1),
        "HR_Upper": np.round(hr_upper, 1),
        "HR_Lower": np.round(hr_lower, 1),
        "SpO2": np.round(spo2_curve, 1),
        "HRV_ms": np.round(hrv_curve, 1),
    })

default_df = generate_patient_multimodal_data()

# Create downloadable CSV template from default data
template_df = pd.DataFrame({
    "Hour": default_df.Hour,
    "Glucose_mg_dL": default_df.Ramadan_Mean,
    "Heart_Rate_bpm": default_df.HR_Mean,
    "SpO2_pct": default_df.SpO2,
    "ECG_HRV_ms": default_df.HRV_ms
})

st.title("📊 Digital Biostatistics Academy (DBA)")
st.caption("Interactive Workforce Upskilling Sandbox • Built for Saudi Vision 2030 Health Transformation")

# --- DATA INGESTION & AUTO-ANALYSIS BAR ---
with st.expander("📂 Data Ingestion Engine: Use Built-in Saudi Cohort or Upload Real Device CSV", expanded=True):
    ing_c1, ing_c2, ing_c3 = st.columns((1.2, 1.5, 1))
    with ing_c1:
        data_source = st.radio(
            "Select Telemetry Source:",
            ("Built-in Saudi Virtual Ward Cohort", "Upload Custom Device CSV")
        )
    with ing_c2:
        uploaded_file = st.file_uploader(
            "Upload CSV (Columns: Hour, Glucose_mg_dL, Heart_Rate_bpm, SpO2_pct, ECG_HRV_ms)",
            type=("csv",)
        )
    with ing_c3:
        st.markdown("**Need a sample file to test?**")
        st.download_button(
            label="⬇️ Download Sample CSV Template",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="saudi_virtual_ward_telemetry.csv",
            mime="text/csv"
        )

# Process Uploaded CSV if selected & provided
using_custom_csv = False
if data_source == "Upload Custom Device CSV" and uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        required_cols = {"Hour", "Glucose_mg_dL"}
        if not required_cols.issubset(set(raw_df.columns)):
            st.error("CSV must include at least 'Hour' and 'Glucose_mg_dL' columns. Click 'Download Sample CSV Template' to see the exact format.")
            df = default_df.copy()
        else:
            raw_df = raw_df.sort_values("Hour").reset_index(drop=True)
            gluc = raw_df["Glucose_mg_dL"].astype(float)
            hr = raw_df["Heart_Rate_bpm"].astype(float) if "Heart_Rate_bpm" in raw_df.columns else pd.Series(np.repeat(74.0, len(raw_df)))
            spo2 = raw_df["SpO2_pct"].astype(float) if "SpO2_pct" in raw_df.columns else pd.Series(np.repeat(97.0, len(raw_df)))
            hrv = raw_df["ECG_HRV_ms"].astype(float) if "ECG_HRV_ms" in raw_df.columns else pd.Series(np.repeat(45.0, len(raw_df)))

            # Auto-compute rolling functional confidence bands
            gluc_std = gluc.rolling(window=4, min_periods=1).std().fillna(12.0)
            hr_std = hr.rolling(window=4, min_periods=1).std().fillna(5.0)

            df = pd.DataFrame({
                "Hour": raw_df["Hour"].astype(float),
                "Standard_Mean": gluc,
                "Standard_Upper": gluc + 1.96 * gluc_std,
                "Standard_Lower": gluc - 1.96 * gluc_std,
                "Ramadan_Mean": gluc,
                "Ramadan_Upper": gluc + 1.96 * gluc_std,
                "Ramadan_Lower": gluc - 1.96 * gluc_std,
                "HR_Mean": hr,
                "HR_Upper": hr + 1.96 * hr_std,
                "HR_Lower": hr - 1.96 * hr_std,
                "SpO2": spo2,
                "HRV_ms": hrv,
            })
            using_custom_csv = True
            st.success(f"✅ Auto-Analysis Complete: Ingested **{len(df)} telemetry timestamps** from `{uploaded_file.name}` and updated all 4 device modules!")
    except Exception as e:
        st.error(f"Could not read CSV file: {e}")
        df = default_df.copy()
else:
    df = default_df.copy()
    if data_source == "Upload Custom Device CSV":
        st.warning("⬆️ Please upload a CSV file above (or download the sample template to test).")

if using_custom_csv:
    st.info(f"👤 **Active Custom Telemetry Stream:** `{uploaded_file.name}` | Records: `{len(df)}` | Auto-modeled across 4 Connected Device Modules")
else:
    st.info(
        "👤 **Active Virtual Care Ward Patient:** `Patient ID: SA-1042` | Age: 48 | Diagnosis: Type-2 Diabetes, Hypertension & Sleep Apnea Risk\n\n"
        "📡 **4 Connected Medical Devices Streaming Live:** `1. CGM Glucose Sensor` • `2. Smartwatch Telemetry` • `3. Wireless Pulse Oximeter (SpO₂)` • `4. Continuous ECG Patch`"
    )

mod1, mod2, mod3, mod4 = st.tabs((
    "🩸 1. CGM Sensor",
    "⌚ 2. Smartwatch (HR)",
    "🫁 3. Pulse Oximeter & ECG Patch",
    "🧠 4. 4-Device Multimodal Fusion"
))

# ==========================================
# MODULE 1: CGM GLUCOSE SENSOR
# ==========================================
with mod1:
    col_ctrl, col_viz = st.columns((1, 2.5))
    with col_ctrl:
        st.markdown("### Device 1: CGM Sensor")
        if using_custom_csv:
            st.caption(f"Analyzing uploaded stream: **{uploaded_file.name}**")
            cohort = "Custom Uploaded Stream"
        else:
            cohort = st.selectbox(
                "Select Patient Condition:",
                ("Ramadan Fasting Protocol (SA-1042)", "Standard Routine Protocol (SA-1042)")
            )
        hypo_thresh = st.slider("Hypoglycemia Threshold (mg/dL)", 55, 85, 70)
        hyper_thresh = st.slider("Hyperglycemia Threshold (mg/dL)", 160, 220, 180)
        show_functional = st.toggle("Enable Digital Biostatistics Curve (FDA)", value=True)

    with col_viz:
        if "Standard" in cohort:
            y_mean, y_up, y_low = df.Standard_Mean, df.Standard_Upper, df.Standard_Lower
        else:
            y_mean, y_up, y_low = df.Ramadan_Mean, df.Ramadan_Upper, df.Ramadan_Lower

        overall_mean = np.mean(y_mean)
        tir = np.mean((y_mean >= hypo_thresh) & (y_mean <= hyper_thresh)) * 100
        hypo_risk = np.mean(y_low < hypo_thresh) * 100

        m1, m2, m3 = st.columns(3)
        m1.metric("Traditional 24h Mean", f"{overall_mean:.1f} mg/dL", "Masks daily swings")
        m2.metric("Time-in-Range (TIR)", f"{tir:.0f}%", delta=f"{tir-70:.0f}% vs Target")
        m3.metric("Hypoglycemia Risk Window", f"{hypo_risk:.0f}%", delta="High Risk" if hypo_risk > 10 else "Low Risk", delta_color="inverse")

        fig = go.Figure()
        fig.add_hrect(y0=hypo_thresh, y1=hyper_thresh, fillcolor="green", opacity=0.08, line_width=0)

        if show_functional:
            fig.add_trace(go.Scatter(
                x=pd.concat((df.Hour, df.Hour.iloc[::-1])),
                y=pd.concat((y_up, y_low.iloc[::-1])),
                fill='toself', fillcolor='rgba(0, 128, 128, 0.2)',
                line=dict(color='rgba(255,255,255,0)'), name='95% Functional Confidence Band'
            ))
            fig.add_trace(go.Scatter(
                x=df.Hour, y=y_mean, mode='lines',
                line=dict(color='#008080', width=3), name='CGM Glucose Trajectory'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df.Hour, y=np.repeat(overall_mean, len(df)), mode='lines',
                line=dict(color='gray', width=3, dash='dash'), name='Traditional Single Mean'
            ))

        fig.update_layout(title="Device 1 Stream: Continuous Glucose Trajectory", xaxis_title="Hour of Day", yaxis_title="Glucose (mg/dL)", height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULE 2: SMARTWATCH HEART RATE
# ==========================================
with mod2:
    c2_left, c2_right = st.columns((1, 2.5))
    with c2_left:
        st.markdown("### Device 2: Smartwatch")
        hr_alert = st.slider("Tachycardia Alert Threshold (bpm)", 75, 105, 85)
        st.markdown("**Biostatistical Method:**\nCircadian Cosinor & Distributional Quantile Modeling")
        st.caption("A single clinic pulse reading (72 bpm) misses autonomic spikes detected by continuous smartwatch streams.")

    with c2_right:
        peak_hr = np.max(df.HR_Mean)
        elevated_pct = np.mean(df.HR_Mean > hr_alert) * 100

        hm1, hm2, hm3 = st.columns(3)
        hm1.metric("Clinic Visit Pulse", "72 bpm", "Single snapshot")
