import streamlit as st
from data import load_data, save_data

st.set_page_config(page_title="Patient Management", layout="wide")

if "name" not in st.session_state or st.session_state["name"] == "":
    st.error("You must log in first")
    st.stop()

data = load_data()
PATIENTS = data["patients"]
USERS = data["users"]

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    .section-title {
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #4a5568;
        border-bottom: 1px solid #21293a;
        padding-bottom: 4px;
        margin-bottom: 10px;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #1c2330 !important;
        border: 1px solid #21293a !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stButton button {
        background-color: #3fb8a0;
        color: #0d1117;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        letter-spacing: 1px;
    }
    .stFormSubmitButton button {
        background-color: #3fb8a0!important;
        color: #0d1117 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    label { color: #7d8590 !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# Top bar
col_a, col_b = st.columns([6, 1])
with col_a:
    st.markdown(f"""
    <div style='padding:10px 0; border-bottom:1px solid #21293a; margin-bottom:20px;'>
        <span style='font-size:1.4rem; font-weight:700; color:white;'>
            Medi<span style='color:#3fb8a0;'>Nova</span>
        </span>
        <span style='color:#7d8590; font-size:0.85rem; margin-left:16px;'>{st.session_state['name']}</span>
        <span style='background:rgba(63,184,160,0.1); border:1px solid #3fb8a0;
                     color:#3fb8a0; padding:3px 10px; border-radius:20px;
                     font-size:0.75rem; margin-left:8px;'>Charge Nurse</span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    if st.button("↩ Logout"):
        st.session_state["name"] = ""
        st.session_state["role"] = ""
        st.switch_page("Streamlit.py")

left, right = st.columns([1.5, 1])

# LEFT — Add New Patient
with left:
    st.markdown("<div class='section-title'>Add New Patient</div>", unsafe_allow_html=True)

    with st.form("add_patient_form"):
        f1, f2 = st.columns(2)
        with f1:
            name = st.text_input("Full Name")
            ward = st.text_input("Ward")
            diagnosis = st.text_area("Diagnosis", height=80)
            allergies = st.text_input("Allergies (if none, type 'None known')")
            medications = st.text_area("Medications (comma separated)", height=80)
            labs = st.text_area("Lab Results", height=68)
        with f2:
            patient_id = st.text_input("Patient ID")
            status = st.selectbox("Status", ["Stable", "Critical", "Recovering"])
            vitals_bp = st.text_input("BP (e.g. 118/76)")
            vitals_hr = st.text_input("Heart Rate (e.g. 72 bpm)")
            vitals_spo2 = st.text_input("SpO2 (e.g. 98%)")
            vitals_pain = st.text_input("Pain Score (e.g. 4/10)")

        notes = st.text_area("Clinical Notes", height=80)

        submitted = st.form_submit_button("➕ Add Patient", use_container_width=True)
        if submitted:
            if name in PATIENTS:
                st.error(f"{name} already exists.")
            elif not name or not patient_id:
                st.error("Name and Patient ID are required.")
            else:
                data["patients"][name] = {
                    "id": patient_id,
                    "ward": ward,
                    "status": status,
                    "condition": diagnosis,
                    "diagnosis": diagnosis,
                    "allergies": allergies,
                    "medications": [m.strip() for m in medications.split(",")],
                    "vitals": {
                        "BP": vitals_bp,
                        "HR": vitals_hr,
                        "SpO2": vitals_spo2,
                        "Pain": vitals_pain
                    },
                    "labs": labs,
                    "notes": notes
                }
                save_data(data)
                st.success(f"Patient {name} added successfully!")

# RIGHT — Current Patients + Remove
with right:
    st.markdown("<div class='section-title'>Current Patients</div>", unsafe_allow_html=True)

    for pname, pdata in PATIENTS.items():
        status = pdata["status"]
        color = '#3fb8a0' if status == "Stable" else '#e05c5c' if status == "Critical" else '#f0a050'
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:12px; margin-bottom:8px;'>
            <div style='color:white; font-size:0.9rem; font-weight:600;'>{pname}</div>
            <div style='color:#7d8590; font-size:0.75rem;'>{pdata['condition']}</div>
            <div style='color:{color}; font-size:0.75rem; margin-top:4px;'>● {status} · {pdata['ward']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Remove Patient</div>", unsafe_allow_html=True)

    patient_to_remove = st.selectbox("", list(PATIENTS.keys()), key="remove_select")

    if st.button("🗑️ Remove Patient", use_container_width=True):
        if patient_to_remove in data["patients"]:
            del data["patients"][patient_to_remove]
            save_data(data)
            st.success(f"{patient_to_remove} removed successfully!")
            st.rerun()
        else:
            st.error("Patient not found.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class'section-title'>Assign Paitent to Doctor</div>", unsafe_allow_html=True)

    doctors = [uname for uname, udata in USERS.items() if udata["role"] == "Doctor"]
    
    a1, a2 = st.columns(2)
    with a1:
        assign_patient = st.selectbox("Paitent", list(PATIENTS.keys()), key="assig_patient")
    with a2:
        assign_doctor = st.selectbox("Doctor", doctors, key="assign_doctor")
    
    if st.button("✅ Assign Doctor", use_container_width=True):
        if "assigments" in data and data ["assigments"]:
           st.markdown("<div class='section-title' style='margin-top:16px;'>Current Assignments</div>", unsafe_allow_html=True)
        for patient, doctor in data["assignments"].items():
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                        padding:10px 12px; margin-bottom:6px; display:flex; justify-content:space-between;'>
                <span style='color:white; font-size:0.85rem;'>{patient}</span>
                <span style='color:#3fb8a0; font-size:0.85rem;'>→ {doctor}</span>
            </div>
            """, unsafe_allow_html=True) 