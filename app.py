import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Digital Biostatistics Academy | KSA",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def generate_patient_multimodal_data():
    np.random.seed(42)
    hours = np.arange(0, 24, 0.25)

    # Device 1: Continuous Glucose Monitor (CGM - mg/dL)
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

    # Device 3: Wireless Pulse Oximeter (SpO2 %) - nocturnal dip around 03:00
    spo2_curve = 97.5 - 3.8 * np.exp(-((hours - 3.0) ** 2) / 2.5) + np.random.normal(0, 0.3, len(hours))
    spo2_curve = np.clip(spo2_curve, 88.0, 99.5)

    # Device 4: Continuous ECG Patch (RMSSD Heart Rate Variability in ms)
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

df = generate_patient_multimodal_data()

st.title("📊 Digital Biostatistics Academy (DBA)")
st.caption("Interactive Workforce Upskilling Sandbox • Built for Saudi Vision 2030 Health Transformation")

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
        cohort = st.selectbox(
            "Select Patient Condition:",
            ("Ramadan Fasting Protocol (SA-1042)", "Standard Routine Protocol (SA-1042)")
        )
        hypo_thresh = st.slider("Hypoglycemia Threshold (mg/dL)", 55, 85, 70)
        hyper_thresh = st.slider("Hyperglycemia Threshold (mg/dL)", 160, 220, 180)
        show_functional = st.toggle("Enable Digital Biostatistics Curve (FDA)", value=True)

    with col_viz:
        if "Ramadan" in cohort:
            y_mean, y_up, y_low = df.Ramadan_Mean, df.Ramadan_Upper, df.Ramadan_Lower
        else:
            y_mean, y_up, y_low = df.Standard_Mean, df.Standard_Upper, df.Standard_Lower

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

        fig.update_layout(title="Device 1 Stream: 24-Hour Continuous Glucose Trajectory", xaxis_title="Hour of Day", yaxis_title="Glucose (mg/dL)", height=360, margin=dict(l=20, r=20, t=40, b=20))
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
        st.caption("A single clinic pulse reading (72 bpm) misses post-meal autonomic spikes detected by continuous smartwatch streams.")

    with c2_right:
        peak_hr = np.max(df.HR_Mean)
        elevated_pct = np.mean(df.HR_Mean > hr_alert) * 100

        hm1, hm2, hm3 = st.columns(3)
        hm1.metric("Clinic Visit Pulse", "72 bpm", "Single snapshot")
        hm2.metric("24h Peak Smartwatch HR", f"{peak_hr:.0f} bpm", "Post-Iftar surge")
        hm3.metric("Time Above Threshold", f"{elevated_pct:.0f}%", delta="Review Beta-Blocker" if elevated_pct > 15 else "Stable", delta_color="inverse")

        fig_hr = go.Figure()
        fig_hr.add_hline(y=hr_alert, line_dash="dot", line_color="red", annotation_text="Alert Threshold")
        fig_hr.add_trace(go.Scatter(
            x=pd.concat((df.Hour, df.Hour.iloc[::-1])),
            y=pd.concat((df.HR_Upper, df.HR_Lower.iloc[::-1])),
            fill='toself', fillcolor='rgba(220, 53, 69, 0.15)',
            line=dict(color='rgba(255,255,255,0)'), name='Wearable Variability Band'
        ))
        fig_hr.add_trace(go.Scatter(
            x=df.Hour, y=df.HR_Mean, mode='lines',
            line=dict(color='#dc3545', width=3), name='Smartwatch Heart Rate (bpm)'
        ))
        fig_hr.update_layout(title="Device 2 Stream: 24-Hour Smartwatch Cardiac Trajectory", xaxis_title="Hour of Day", yaxis_title="Heart Rate (bpm)", height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hr, use_container_width=True)

# ==========================================
# MODULE 3: PULSE OXIMETER & CONTINUOUS ECG PATCH
# ==========================================
with mod3:
    c3_left, c3_right = st.columns((1, 2.5))
    with c3_left:
        st.markdown("### Devices 3 & 4: Oximeter & ECG Patch")
        spo2_thresh = st.slider("Nocturnal Desaturation Alert (SpO₂ %)", 90, 96, 94)
        hrv_thresh = st.slider("Low HRV Autonomic Stress Alert (ms)", 20, 45, 30)
        st.markdown("**Biostatistical Method:**\nJoint Functional Threshold & Event-Rate Modeling")
        st.caption("Daytime clinic SpO₂ (98%) looks normal, but overnight wireless oximetry + ECG patch HRV reveal nocturnal hypoxia and autonomic stress.")

    with c3_right:
        min_spo2 = np.min(df.SpO2)
        desat_mins = int(np.sum(df.SpO2 < spo2_thresh) * 15)
        min_hrv = np.min(df.HRV_ms)

        om1, om2, om3 = st.columns(3)
        om1.metric("Daytime Clinic SpO₂", "98.0%", "Misses sleep apnea")
        om2.metric("Overnight Nadir SpO₂ (Device 3)", f"{min_spo2:.1f}%", delta=f"{desat_mins} mins < {spo2_thresh}%", delta_color="inverse")
        om3.metric("Lowest ECG Patch HRV (Device 4)", f"{min_hrv:.0f} ms", delta="Autonomic Stress" if min_hrv < hrv_thresh else "Normal", delta_color="inverse")

        fig_ox = go.Figure()
        fig_ox.add_trace(go.Scatter(x=df.Hour, y=df.SpO2, mode='lines', name='Wireless Pulse Oximeter (SpO₂ %)', line=dict(color='#0d6efd', width=3)))
        fig_ox.add_trace(go.Scatter(x=df.Hour, y=df.HRV_ms, mode='lines', name='ECG Patch HRV (RMSSD ms)', line=dict(color='#fd7e14', width=3, dash='dot'), yaxis="y2"))
        fig_ox.add_hline(y=spo2_thresh, line_dash="dash", line_color="#0d6efd", annotation_text="SpO₂ Alert")

        fig_ox.update_layout(
            title="Devices 3 & 4 Streams: Overnight Pulse Oximetry (SpO₂) & ECG Patch HRV",
            xaxis_title="Hour of Day",
            yaxis=dict(title="SpO₂ (%)", range=(88, 100)),
            yaxis2=dict(title="ECG HRV (ms)", overlaying="y", side="right", range=(10, 90)),
            height=360,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_ox, use_container_width=True)

# ==========================================
# MODULE 4: 4-DEVICE MULTIMODAL RISK FUSION
# ==========================================
with mod4:
    st.markdown("### 4-Device Multimodal Fusion & Micro-Randomized Trial Simulator")
    st.write("Simulate how combining **all 4 connected medical devices** (CGM + Smartwatch + Pulse Oximeter + ECG Patch) enables precision timing of a **16:00 Virtual Ward Intervention**.")

    nudge_active = st.toggle("🚀 Activate 4-Device Closed-Loop Virtual Ward Intervention", value=False)

