import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="B2B Enterprise Portal | DBA", page_icon="🏥", layout="wide")

st.title("🏥 Enterprise Workforce Analytics & B2B SaaS Portal")
st.markdown("Empowering Saudi hospitals, virtual care centers, and biotech hubs to build in-house Digital Biostatistics capacity.")

b_col1, b_col2 = st.columns((2, 1))
org_name = b_col1.selectbox(
    "Select Enterprise Client View:",
    (
        "Seha Virtual Hospital — National Remote Care",
        "King Faisal Specialist Hospital & Research Centre",
        "Eastern Province & Jubail Health Cluster"
    )
)
quarter = b_col2.selectbox("Reporting Period:", ("Q4 2026 (Current)", "Q3 2026", "Full Year 2026"))

# Dynamic client profiles so every selection updates the entire dashboard
if "Seha" in org_name:
    clinicians, cert_rate, studies, saved_sar = 680, 88, 27, 2.35
    trained_pct = (94, 89, 96, 78, 85)
    trials_count = (9, 7, 6, 2, 3)
    default_seats = 650
elif "King Faisal" in org_name:
    clinicians, cert_rate, studies, saved_sar = 420, 91, 22, 1.85
    trained_pct = (92, 88, 98, 86, 90)
    trials_count = (5, 4, 7, 4, 2)
    default_seats = 400
else:
    clinicians, cert_rate, studies, saved_sar = 290, 79, 14, 1.05
    trained_pct = (86, 81, 84, 68, 76)
    trials_count = (4, 3, 3, 2, 2)
    default_seats = 300

# Adjust numbers slightly when switching reporting periods
if "Q3" in quarter:
    clinicians = int(clinicians * 0.85)
    cert_rate = cert_rate - 6
    studies = max(5, studies - 5)
    saved_sar = round(saved_sar * 0.8, 2)
elif "Full Year" in quarter:
    studies = int(studies * 1.4)
    saved_sar = round(saved_sar * 3.6, 2)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Active Licensed Clinicians", f"{clinicians}", "+15% vs prior period")
k2.metric("SCFHS CPD Certification Rate", f"{cert_rate}%", "+6% improvement")
k3.metric("Validated AI & Wearable Studies", f"{studies}", "Active across 5 wards")
k4.metric("Consulting Fees Saved (Est.)", f"SAR {saved_sar:.2f}M", "3.8x Annual ROI")

st.divider()

chart_col, table_col = st.columns((1.3, 1.2))
depts = ("Endocrinology", "Cardiology", "Clinical Trials", "Oncology", "Digital Health IT")

with chart_col:
    st.markdown(f"#### Competency Readiness — {org_name}")
    fig_b2b = go.Figure()
    fig_b2b.add_trace(go.Bar(
        x=depts,
        y=trained_pct,
        marker_color="#008080",
        text=trained_pct,
        texttemplate="%{text}%",
        textposition="outside"
    ))
    fig_b2b.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="Vision 2030 Target (80%)")
    fig_b2b.update_layout(yaxis_range=(0, 110), yaxis_title="Certified Staff (%)", height=320, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_b2b, use_container_width=True)

with table_col:
    st.markdown("#### Live Clinical Impact & Skill Audit")
    dept_data = pd.DataFrame({
        "Department": depts,
        "Certified (%)": trained_pct,
        "Active Digital Trials": trials_count,
        "Top Track": ("CGM & Functional Data", "Wearable ECG/HRV", "Adaptive N-of-1 Trials", "Multimodal Biomarkers", "AI Model Validation")
    })
    st.dataframe(dept_data, use_container_width=True, hide_index=True)

st.divider()
st.markdown("#### 💰 B2B SaaS Licensing & Hospital ROI Calculator (Investor View)")
roi_c1, roi_c2, roi_c3 = st.columns(3)
seats = roi_c1.slider("Number of Clinician / Researcher Seats", 50, 1000, default_seats, step=50)
annual_license = seats * 1800
est_savings = seats * 5200
roi_c2.metric("Annual B2B SaaS Subscription", f"SAR {annual_license:,.0f} / yr", "Enterprise Tier")
roi_c3.metric("Estimated Hospital Net Savings", f"SAR {est_savings - annual_license:,.0f} / yr", f"{est_savings / annual_license:.1f}x ROI")
