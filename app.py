import os
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# Import core modules
from validator import (
    load_data,
    check_interactions,
    check_allergies,
    get_side_effects,
    calculate_condition_risk,
    calculate_rule_risk
)
from train_model import train_and_save_model
from ai_engine import (
    suggest_drug_corrections,
    calculate_ai_risk_score,
    generate_ai_clinical_narrative
)
from auth import login_user, logout_user, is_authenticated, DEMO_USERS
from patient_manager import load_patients, save_patient

# Page Configuration
st.set_page_config(
    page_title="CHS Clinical Portal | Corporate Trust",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Aggressive Custom CSS Overrides targeting Streamlit Internal DOM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Font Override */
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Force Light Theme Base (Slate 50) */
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.8) !important;
    }

    /* Corporate Trust Dual-Tone Hero Banner */
    .corporate-hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        border-radius: 20px !important;
        padding: 2.2rem 2.6rem !important;
        color: #FFFFFF !important;
        box-shadow: 0 12px 30px -5px rgba(79, 70, 229, 0.35) !important;
        margin-bottom: 1.8rem !important;
        position: relative !important;
    }

    .hero-title-text {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0 !important;
        letter-spacing: -0.03em !important;
    }

    .hero-subtitle-text {
        font-size: 1.1rem !important;
        color: #EEF2FF !important;
        margin-top: 0.4rem !important;
        font-weight: 500 !important;
    }

    /* Primary Button Overrides (Gradient Lift) */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.35) !important;
        transition: all 0.2s ease-out !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px 0 rgba(79, 70, 229, 0.5) !important;
    }

    /* Card Containers */
    .trust-card-elevated {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.6rem !important;
        margin-bottom: 1.4rem !important;
        box-shadow: 0 4px 20px -2px rgba(79, 70, 229, 0.08) !important;
        transition: all 0.2s ease-out !important;
    }

    .trust-card-elevated:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px -5px rgba(79, 70, 229, 0.16) !important;
    }

    /* Patient Vitals Card */
    .patient-vitals-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 6px solid #4F46E5 !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.6rem !important;
        box-shadow: 0 4px 20px -2px rgba(79, 70, 229, 0.09) !important;
    }

    /* Streamlit Input Overrides */
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
    }

    div[data-baseweb="input"] > div:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }

    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.8rem !important;
        box-shadow: 0 4px 20px -2px rgba(79, 70, 229, 0.1) !important;
    }

    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px -2px rgba(79, 70, 229, 0.06) !important;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 4px 18px -2px rgba(79, 70, 229, 0.08) !important;
    }

    /* Status Badges */
    .badge-success-trust {
        background-color: #ECFDF5 !important;
        color: #065F46 !important;
        border: 2px solid #10B981 !important;
        padding: 0.85rem 1.2rem !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        text-align: center !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.2) !important;
    }

    .badge-warning-trust {
        background-color: #FFFBEB !important;
        color: #92400E !important;
        border: 2px solid #F59E0B !important;
        padding: 0.85rem 1.2rem !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        text-align: center !important;
        box-shadow: 0 4px 14px 0 rgba(245, 158, 11, 0.2) !important;
    }

    .badge-critical-trust {
        background-color: #FEF2F2 !important;
        color: #991B1B !important;
        border: 2px solid #EF4444 !important;
        padding: 0.85rem 1.2rem !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        text-align: center !important;
        box-shadow: 0 4px 14px 0 rgba(239, 68, 68, 0.2) !important;
    }

    .ai-narrative-box {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%) !important;
        border: 1px solid #C4B5FD !important;
        border-radius: 16px !important;
        padding: 1.5rem 1.8rem !important;
        margin-bottom: 1.5rem !important;
        color: #4C1D95 !important;
        box-shadow: 0 4px 20px -2px rgba(124, 58, 237, 0.12) !important;
    }

    /* Tab Custom Styling */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        color: #64748B !important;
    }

    button[aria-selected="true"] {
        color: #4F46E5 !important;
        background-color: #EEF2FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cache Model Payload
@st.cache_resource
def get_ml_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'model', 'prescription_risk_model.pkl')
    if not os.path.exists(model_path):
        train_and_save_model()
    try:
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading ML model: {e}")
        return None

drugs_df, interactions_df, side_effects_df = load_data()
model_payload = get_ml_model()
patients_df = load_patients()

known_drugs = []
if not drugs_df.empty and 'drug_name' in drugs_df.columns:
    known_drugs = sorted(drugs_df['drug_name'].dropna().unique().tolist())

# =========================================================
# LOGIN PAGE
# =========================================================
if not is_authenticated():
    st.markdown("<br>", unsafe_allow_html=True)
    l_col1, l_col2, l_col3 = st.columns([1, 1.8, 1])

    with l_col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-block; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 1.2rem; border-radius: 24px; box-shadow: 0 12px 30px -5px rgba(79,70,229,0.4); color: #FFFFFF; font-size: 3rem; margin-bottom: 1rem;">
                🏥
            </div>
            <h1 style="color: #0F172A; margin-bottom: 0.2rem; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">Centralized Healthcare System</h1>
            <p style="color: #64748B; font-size: 1.1rem; font-weight: 500;">Clinical Prescription Validation & AI Portal</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<h3 style='color:#0F172A; font-weight:700; margin-bottom: 1rem;'>🔐 Clinician Portal Sign-In</h3>", unsafe_allow_html=True)
            user_input = st.text_input("Username", value="dr_fleming", placeholder="e.g. dr_fleming")
            pass_input = st.text_input("Password", type="password", value="demo123")
            submit_login = st.form_submit_button("Sign In to Clinical Portal", use_container_width=True, type="primary")

            if submit_login:
                if user_input:
                    success, msg = login_user(user_input, pass_input)
                    if success:
                        st.success("Authentication successful! Redirecting...")
                        st.rerun()
                else:
                    st.error("Please enter a username.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h5 style='color:#0F172A; font-weight:700; margin-bottom: 0.6rem;'>⚡ 1-Click Demo Clinician Profiles</h5>", unsafe_allow_html=True)
        d_col1, d_col2, d_col3 = st.columns(3)

        if d_col1.button("👨‍⚕️ Dr. Fleming\n(Cardiologist)", use_container_width=True):
            login_user("dr_fleming", is_demo=True)
            st.rerun()

        if d_col2.button("👩‍⚕️ Dr. Blackwell\n(Pharmacist)", use_container_width=True):
            login_user("dr_blackwell", is_demo=True)
            st.rerun()

        if d_col3.button("🩺 Dr. House\n(Diagnostics)", use_container_width=True):
            login_user("dr_house", is_demo=True)
            st.rerun()

    st.stop()

# =========================================================
# LOGGED IN CLINICIAN PORTAL
# =========================================================
user_data = st.session_state.get("current_user", {})

# Sidebar Navigation Control
with st.sidebar:
    st.markdown(f"### {user_data.get('avatar', '👨‍⚕️')} Clinician Profile")
    st.markdown(f"**{user_data.get('name', 'Clinician')}**")
    st.caption(f"{user_data.get('role', 'Physician')} | {user_data.get('department', 'Clinical Care')}")
    st.markdown("Status: <span style='color:#10B981; font-weight:700;'>● Active Session</span>", unsafe_allow_html=True)

    if st.button("🚪 Logout Clinician"):
        logout_user()
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🌐 Free Online AI Key (Optional)")
    st.caption("Google Gemini 1.5 Flash Free API Key. *(Left empty = local intelligent AI engine)*.")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")

    st.markdown("---")
    st.info("CHS Portal v5.5 | Corporate Trust Design System")

# Corporate Trust Dual-Tone Hero Banner Header
st.markdown(f"""
<div class="corporate-hero-banner">
    <div style="float: right; text-align: right;">
        <span style="background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); padding: 0.5rem 1.1rem; border-radius: 20px; font-size: 0.95rem; color: #FFFFFF; font-weight:700;">
            {user_data.get('avatar')} {user_data.get('name')}
        </span>
    </div>
    <div class="hero-title-text">🏥 CHS Prescription Validation & AI Hub</div>
    <div class="hero-subtitle-text">Centralized Healthcare System — Enterprise Clinical Decision Support Portal</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5 WELL-STRUCTURED CLINICAL PAGES
# ---------------------------------------------------------
page_nav = st.tabs([
    "🏥 Clinical Workspace",
    "📊 AI Safety & Risk Analysis",
    "🤖 AI Clinical Narrative",
    "📚 Drug Directory & Matrix",
    "📄 Certificate Exporter"
])

# =========================================================
# PAGE 1: CLINICAL WORKSPACE
# =========================================================
with page_nav[0]:
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>👤 Step 1: Select Patient Profile</h3>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns([1.6, 1])

    with p_col1:
        patient_options = [f"{row['patient_id']} - {row['name']} ({row['age']}y, {row['gender']})" for _, row in patients_df.iterrows()]
        selected_p_str = st.selectbox("Select Patient from Hospital Registry", patient_options)
        selected_idx = patient_options.index(selected_p_str)
        curr_patient = patients_df.iloc[selected_idx].to_dict()

    with p_col2:
        with st.expander("➕ Register New Patient Profile"):
            with st.form("new_patient_form"):
                np_name = st.text_input("Full Name", placeholder="e.g. Alice Smith")
                np_age = st.number_input("Age", min_value=1, max_value=120, value=45)
                np_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                np_allergies = st.text_input("Allergies", value="None")
                np_condition = st.text_input("Diagnosis / Condition", value="Hypertension")
                np_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                np_submit = st.form_submit_button("Save Patient to Registry")

                if np_submit and np_name:
                    new_p = {
                        "patient_id": f"P00{len(patients_df)+1}",
                        "name": np_name,
                        "age": np_age,
                        "gender": np_gender,
                        "allergies": np_allergies,
                        "condition": np_condition,
                        "blood_group": np_blood,
                        "bp": "120/80 mmHg",
                        "heart_rate": "72 bpm"
                    }
                    save_patient(new_p)
                    st.success(f"Patient {np_name} registered successfully!")
                    st.rerun()

    # Corporate Patient Vitals Profile Card
    st.markdown(f"""
    <div class="patient-vitals-card">
        <div style="font-size: 1.4rem; font-weight: 800; color: #4F46E5;">
            🪪 Active Patient Record: {curr_patient['name']} ({curr_patient['patient_id']})
        </div>
        <div style="display: flex; gap: 2rem; margin-top: 0.8rem; flex-wrap: wrap; color: #334155; font-size: 1rem;">
            <div><strong>Age:</strong> {curr_patient['age']} years</div>
            <div><strong>Gender:</strong> {curr_patient['gender']}</div>
            <div><strong>Blood Group:</strong> <span style="color:#10B981; font-weight:800;">{curr_patient['blood_group']}</span></div>
            <div><strong>Recorded Allergies:</strong> <span style="color:#EF4444; font-weight:800;">{curr_patient['allergies']}</span></div>
            <div><strong>Diagnosis:</strong> {curr_patient['condition']}</div>
            <div><strong>Vitals:</strong> BP {curr_patient.get('bp', '120/80')} | HR {curr_patient.get('heart_rate', '72 bpm')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>💊 Step 2: Build Prescription</h3>", unsafe_allow_html=True)

    if 'prescription' not in st.session_state:
        st.session_state.prescription = [
            {"name": "Warfarin", "dose": "5 mg"},
            {"name": "Aspirin", "dose": "100 mg"}
        ]

    w_col1, w_col2 = st.columns([1, 1.25])

    with w_col1:
        st.markdown('<div class="trust-card-elevated">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>Add Drug Entry</h4>", unsafe_allow_html=True)
        med_select_mode = st.radio("Search Mode", ["Database Search", "Custom Drug Name"], horizontal=True)

        if med_select_mode == "Database Search" and known_drugs:
            med_name_input = st.selectbox("Select Drug", known_drugs)
        else:
            med_name_input = st.text_input("Drug Name", placeholder="E.g. Warfarin, Aspirne (supports AI typo check)")

        med_dose_input = st.text_input("Dose / Frequency", value="500 mg", placeholder="E.g. 500 mg once daily")

        # AI Fuzzy Typo Correction Check
        suggested_drug, typo_confidence = suggest_drug_corrections(med_name_input, known_drugs)
        if med_name_input and suggested_drug != med_name_input and typo_confidence >= 65.0:
            st.info(f"🤖 **AI Typo Assistant:** Did you mean **'{suggested_drug}'**? ({typo_confidence}% similarity match)")
            if st.button(f"Use AI Suggestion: {suggested_drug}"):
                med_name_input = suggested_drug

        if st.button("➕ Add to Prescription", use_container_width=True, type="primary"):
            clean_name = med_name_input.strip() if med_name_input else ""
            clean_dose = med_dose_input.strip() if med_dose_input else ""

            if not clean_name:
                st.error("Please enter a valid drug name.")
            else:
                existing_names = [m["name"].lower() for m in st.session_state.prescription]
                if clean_name.lower() in existing_names:
                    st.warning(f"'{clean_name}' is already in the prescription list.")
                else:
                    st.session_state.prescription.append({"name": clean_name, "dose": clean_dose})
                    st.success(f"Added {clean_name} ({clean_dose}).")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with w_col2:
        st.markdown('<div class="trust-card-elevated">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>Prescribed Medicines List</h4>", unsafe_allow_html=True)

        if not st.session_state.prescription:
            st.info("No medicines added. Add at least one drug to validate.")
        else:
            for idx, item in enumerate(st.session_state.prescription):
                m_col1, m_col2, m_col3 = st.columns([3, 2, 1])
                m_col1.write(f"**{idx + 1}. {item['name']}**")
                m_col2.write(f"`{item['dose']}`" if item['dose'] else "*No dose*")
                if m_col3.button("❌", key=f"del_{idx}"):
                    st.session_state.prescription.pop(idx)
                    st.rerun()

            if st.button("🗑️ Clear Prescription"):
                st.session_state.prescription = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Next Step:** Click on **'📊 AI Safety & Risk Analysis'** tab above to view full clinical risk results.")

# Perform Validation Computation for downstream pages
med_list = [item["name"] for item in st.session_state.prescription]
p_age = int(curr_patient['age'])
p_gender = str(curr_patient['gender'])
p_allergies = str(curr_patient['allergies'])
p_condition = str(curr_patient['condition'])

found_interactions, pairs_without_interaction = check_interactions(med_list, interactions_df)
allergy_conflicts = check_allergies(med_list, p_allergies)
side_effects_dict = get_side_effects(med_list, side_effects_df)
condition_risk_factor = calculate_condition_risk(p_condition)
rule_risk = calculate_rule_risk(found_interactions, allergy_conflicts)

ml_risk_str = "UNKNOWN"
ml_probs = [0.33, 0.33, 0.34]
feat_imp_dict = {}

if model_payload and 'model' in model_payload:
    clf = model_payload['model']
    feat_cols = model_payload.get('feature_cols', [])
    feat_imp_dict = model_payload.get('feature_importances', {})

    is_elderly = 1 if p_age >= 65 else 0
    num_meds = len(med_list)
    num_inter = len(found_interactions)
    has_all = 1 if allergy_conflicts else 0
    num_se = sum(len(v) for v in side_effects_dict.values())

    max_sev = 0
    if any(i['severity'] == 'HIGH' for i in found_interactions):
        max_sev = 3
    elif any(i['severity'] == 'MODERATE' for i in found_interactions):
        max_sev = 2
    elif any(i['severity'] == 'LOW' for i in found_interactions):
        max_sev = 1

    input_df = pd.DataFrame([{
        'patient_age': p_age,
        'is_elderly': is_elderly,
        'num_medicines': num_meds,
        'has_allergy_conflict': has_all,
        'max_interaction_severity': max_sev,
        'total_interaction_count': num_inter,
        'total_side_effects_count': num_se,
        'condition_risk_factor': condition_risk_factor
    }])[feat_cols]

    try:
        pred_class = clf.predict(input_df)[0]
        probs = clf.predict_proba(input_df)[0]
        risk_map = {0: 'LOW', 1: 'MODERATE', 2: 'HIGH'}
        ml_risk_str = risk_map.get(pred_class, 'LOW')

        if len(probs) == 3:
            ml_probs = probs
        else:
            ml_probs = [0.0, 0.0, 0.0]
            for c_idx, c_label in enumerate(clf.classes_):
                ml_probs[c_label] = probs[c_idx]
    except Exception as e:
        ml_risk_str = f"Error ({e})"

ai_risk_score, ai_risk_category = calculate_ai_risk_score(
    ml_probs, found_interactions, allergy_conflicts, p_age, condition_risk_factor
)

if allergy_conflicts or any(i['severity'] == 'HIGH' for i in found_interactions):
    final_risk = "HIGH"
elif any(i['severity'] == 'MODERATE' for i in found_interactions):
    final_risk = "MODERATE"
else:
    final_risk = ml_risk_str if ml_risk_str in ["LOW", "MODERATE", "HIGH"] else rule_risk

# =========================================================
# PAGE 2: AI SAFETY & RISK ANALYSIS
# =========================================================
with page_nav[1]:
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>📊 AI Safety & Clinical Risk Dashboard</h3>", unsafe_allow_html=True)

    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        st.caption("Final Combined Risk Level")
        if final_risk == "HIGH":
            st.markdown('<div class="badge-critical-trust">🚨 HIGH RISK</div>', unsafe_allow_html=True)
        elif final_risk == "MODERATE":
            st.markdown('<div class="badge-warning-trust">⚠️ MODERATE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-success-trust">✅ LOW RISK</div>', unsafe_allow_html=True)

    with r_col2:
        st.caption("Random Forest ML Model Prediction")
        if ml_risk_str == "HIGH":
            st.markdown('<div class="badge-critical-trust">🤖 HIGH</div>', unsafe_allow_html=True)
        elif ml_risk_str == "MODERATE":
            st.markdown('<div class="badge-warning-trust">🤖 MODERATE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-success-trust">🤖 LOW</div>', unsafe_allow_html=True)

    with r_col3:
        st.caption("Unified AI Risk Index Gauge")
        st.metric("AI Risk Score", f"{ai_risk_score} / 100", delta=ai_risk_category, delta_color="inverse" if ai_risk_score >= 40 else "normal")

    st.progress(float(ai_risk_score / 100.0))
    st.markdown("---")

    st.markdown("<h4 style='color:#0F172A; font-weight:800;'>1. Drug Interaction Check</h4>", unsafe_allow_html=True)
    if found_interactions:
        for inter in found_interactions:
            sev_color = "#EF4444" if inter['severity'] == "HIGH" else "#F59E0B" if inter['severity'] == "MODERATE" else "#10B981"
            st.markdown(f"""
            <div class="trust-card-elevated">
                <div style="font-size:1.25rem; font-weight:800; color:#0F172A;">🔀 {inter['drug_a']} + {inter['drug_b']}</div>
                <div style="color:{sev_color}; font-weight:800; margin-top:0.3rem; font-size:1.05rem;">Severity: {inter['severity']}</div>
                <div style="margin-top:0.5rem; color:#475569; font-size:1rem;"><strong>Clinical Effect:</strong> {inter['effect']}</div>
                <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-left:4px solid #10B981; padding:0.8rem 1rem; border-radius:10px; margin-top:0.8rem; color:#065F46;">
                    <strong>💡 Recommended Safer Alternative:</strong> {inter.get('safer_alternative', 'N/A')}<br/>
                    <small><strong>Clinical Rationale:</strong> {inter.get('rationale', 'N/A')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No known drug interaction found in the supplied dataset.")

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>2. Patient Allergy Alerts</h4>", unsafe_allow_html=True)
        if allergy_conflicts:
            for ac in allergy_conflicts:
                st.error(f"🚨 {ac['message']}")
        else:
            st.success("✅ No allergy conflicts detected.")

    with s2:
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>3. Known Drug Side Effects</h4>", unsafe_allow_html=True)
        has_se = False
        for med, se_list in side_effects_dict.items():
            if se_list:
                has_se = True
                st.write(f"**{med}:** " + ", ".join([f"`{se}`" for se in se_list]))
        if not has_se:
            st.write("No recorded side effects found.")

# =========================================================
# PAGE 3: AI CLINICAL NARRATIVE
# =========================================================
with page_nav[2]:
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>🤖 AI Clinical Narrative & Deep Analysis</h3>", unsafe_allow_html=True)
    ai_narrative = generate_ai_clinical_narrative(
        p_age, p_gender, p_condition, med_list, found_interactions, p_allergies, final_risk, gemini_key
    )
    st.markdown(f'<div class="ai-narrative-box">{ai_narrative}</div>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>🤖 Random Forest Class Probabilities</h4>", unsafe_allow_html=True)
        prob_df = pd.DataFrame({
            "Risk Category": ["Low Risk", "Moderate Risk", "High Risk"],
            "Probability (%)": [ml_probs[0]*100, ml_probs[1]*100, ml_probs[2]*100]
        })
        st.bar_chart(prob_df.set_index("Risk Category"))

    with c2:
        st.markdown("<h4 style='color:#0F172A; font-weight:800;'>🔍 ML Feature Importance Weights</h4>", unsafe_allow_html=True)
        if feat_imp_dict:
            imp_df = pd.DataFrame(list(feat_imp_dict.items()), columns=["Feature", "Weight"]).sort_values("Weight", ascending=False)
            st.bar_chart(imp_df.set_index("Feature"))

# =========================================================
# PAGE 4: DRUG KNOWLEDGEBASE
# =========================================================
with page_nav[3]:
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>📚 Hospital Drug Knowledgebase & Interaction Matrix</h3>", unsafe_allow_html=True)
    k_tab1, k_tab2, k_tab3 = st.tabs(["Drugs Directory", "Interactions Matrix", "Side Effects Database"])

    with k_tab1:
        st.dataframe(drugs_df, use_container_width=True)

    with k_tab2:
        st.dataframe(interactions_df, use_container_width=True)

    with k_tab3:
        st.dataframe(side_effects_df, use_container_width=True)

# =========================================================
# PAGE 5: CERTIFICATE EXPORTER
# =========================================================
with page_nav[4]:
    st.markdown("<h3 style='color:#0F172A; font-weight:800;'>📄 Official Prescription Certificate Exporter</h3>", unsafe_allow_html=True)

    report_text = f"""==================================================
CENTRALIZED HEALTHCARE SYSTEM (CHS)
OFFICIAL PRESCRIPTION & SAFETY CERTIFICATE
==================================================
Attending Clinician: {user_data.get('name')} ({user_data.get('role')})
Department: {user_data.get('department')}
--------------------------------------------------
PATIENT PROFILE:
Patient Name: {curr_patient['name']} (ID: {curr_patient['patient_id']})
Age / Gender: {p_age} years | {p_gender}
Blood Group: {curr_patient.get('blood_group')}
Recorded Allergies: {p_allergies}
Diagnosis: {p_condition}
--------------------------------------------------
PRESCRIBED MEDICINES:
{chr(10).join([f"- {m['name']} ({m['dose']})" for m in st.session_state.prescription])}
--------------------------------------------------
CLINICAL SAFETY AUDIT:
Final Combined Risk Level: {final_risk}
Random Forest ML Risk: {ml_risk_str}
AI Risk Score Index: {ai_risk_score} / 100 ({ai_risk_category})

INTERACTION AUDIT:
{chr(10).join([f"- {i['drug_a']} + {i['drug_b']} [{i['severity']}]: {i['effect']} (Safer Alt: {i['safer_alternative']})" for i in found_interactions]) if found_interactions else "No critical drug interactions found."}

ALLERGY CONFLICT AUDIT:
{chr(10).join([f"- {ac['message']}" for ac in allergy_conflicts]) if allergy_conflicts else "No patient allergy conflicts detected."}
==================================================
DISCLAIMER: Prototype decision support system.
==================================================
"""
    st.code(report_text, language="text")

    st.download_button(
        label="📥 Download Formal Clinical Certificate (TXT)",
        data=report_text,
        file_name=f"clinical_prescription_certificate_{curr_patient['patient_id']}.txt",
        mime="text/plain",
        type="primary"
    )
