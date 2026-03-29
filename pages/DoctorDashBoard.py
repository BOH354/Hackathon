import streamlit as st
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="NovaMed Dashboard", layout="wide")

st_autorefresh(interval=30000, key="vitals_refresh")

if "name" not in st.session_state or st.session_state["name"] == "":
    st.error("You must log in first")
    st.stop()

if "selected_patient" not in st.session_state:
    st.session_state["selected_patient"] = ""
if "requests" not in st.session_state:
    st.session_state["requests"] = []

from data import load_data, save_data

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
                     font-size:0.75rem; margin-left:8px;'>Doctor</span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    if st.button("↩ Logout"):
        st.session_state["name"] = ""
        st.session_state["role"] = ""
        st.switch_page("streamlit.py")

left, middle, right = st.columns([1.5, 3, 1.5])

# LEFT — Patient List
with left:
    data = load_data()
    PATIENTS = data["patients"]
    st.markdown("<div class='section-title'>My Patients</div>", unsafe_allow_html=True)

    if not PATIENTS:
        st.markdown("""
        <div style='color:#4a5568; font-size:0.8rem; padding:12px;'>
            No active patients.
        </div>
        """, unsafe_allow_html=True)
    else:
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
            if st.button(f"View {pname}", key=f"btn_{pname}", use_container_width=True):
                st.session_state["selected_patient"] = pname

# MIDDLE — Patient Records
with middle:
    data = load_data()
    PATIENTS = data["patients"]

    if not PATIENTS:
        st.markdown("""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:24px; text-align:center; color:#7d8590; margin-top:20px;'>
            <div style='font-size:2rem; margin-bottom:8px;'>🏥</div>
            <div style='font-size:0.9rem;'>No active patients.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    if st.session_state["selected_patient"] not in PATIENTS:
        st.session_state["selected_patient"] = list(PATIENTS.keys())[0]

    p = PATIENTS[st.session_state["selected_patient"]]
    pname = st.session_state["selected_patient"]

    st.markdown(f"<div class='section-title'>Patient Record — {pname}</div>", unsafe_allow_html=True)

    status = p["status"]
    colour = "#3fb8a0" if status == "Stable" else "#e05c5c" if status == "Critical" else "#f0a050"
    st.markdown(f"""
    <div style='background:#161b22; border:1px solid #21293a; border-radius:8px; padding:16px; margin-bottom:12px;'>
        <span style='font-size:1.1rem; font-weight:700; color:white;'>{pname}</span>
        <span style='color:#7d8590; font-size:0.8rem; margin-left:10px;'>{p['id']} · {p['ward']}</span>
        <span style='color:{colour}; font-size:0.8rem; margin-left:10px;'>● {status}</span>
        <div style='color:#e6edf3; margin-top:8px; font-size:0.85rem;'>{p['diagnosis']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Live Vitals
    st.markdown("<div class='section-title'>Vitals — Live</div>", unsafe_allow_html=True)
    try:
        base_hr = int(p["vitals"]["HR"].split()[0])
        base_bp_sys = int(p["vitals"]["BP"].split("/")[0])
        base_bp_dia = int(p["vitals"]["BP"].split("/")[1])
        base_spo2 = int(p["vitals"]["SpO2"].replace("%", ""))
        base_pain = p["vitals"]["Pain"]

        live_hr = base_hr + random.randint(-3, 3)
        live_bp = f"{base_bp_sys + random.randint(-3, 3)}/{base_bp_dia + random.randint(-2, 2)}"
        live_spo2 = base_spo2 + random.randint(-1, 1)

        vitals_live = [
            ("BP", live_bp),
            ("HR", f"{live_hr} bpm"),
            ("SpO2", f"{live_spo2}%"),
            ("Pain", base_pain),
        ]
    except:
        vitals_live = [(k, v) for k, v in p["vitals"].items()]

    v1, v2, v3, v4 = st.columns(4)
    for col, (key, val) in zip([v1, v2, v3, v4], vitals_live):
        with col:
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                        padding:12px; text-align:center;'>
                <div style='font-size:0.65rem; color:#4a5568; text-transform:uppercase; letter-spacing:1px;'>{key}</div>
                <div style='font-size:1.3rem; font-weight:700; color:#3fb8a0;'>{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Medications
    st.markdown("<div class='section-title'>Medications</div>", unsafe_allow_html=True)
    for med in p["medications"]:
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-left:3px solid #3fb8a0;
                    border-radius:6px; padding:10px 14px; margin-bottom:6px; color:#e6edf3; font-size:0.85rem;'>
            💊 {med}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Admission Document
    st.markdown("<div class='section-title'>Admission Document</div>", unsafe_allow_html=True)
    try:
        with open("documents/admission_blank.pdf", "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📄 Download Admission Document",
            data=pdf_bytes,
            file_name="admission_document.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except:
        st.markdown("""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:6px;
                    padding:10px 14px; color:#4a5568; font-size:0.85rem;'>
            📄 No document on file
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Allergies
    st.markdown("<div class='section-title'>Allergies</div>", unsafe_allow_html=True)
    allergy_color = "#e05c5c" if p["allergies"] != "None known" else "#3fb8a0"
    st.markdown(f"""
    <div style='background:#161b22; border:1px solid #21293a; border-radius:6px;
                padding:10px 14px; color:{allergy_color}; font-size:0.85rem;'>
        ⚠️ {p['allergies']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Labs
    st.markdown("<div class='section-title'>Latest Lab Result</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#161b22; border:1px solid #21293a; border-radius:6px;
                padding:10px 14px; color:#e6edf3; font-size:0.85rem;'>
        🧪 {p['labs']}
    </div>
    """, unsafe_allow_html=True)

# RIGHT — Requests + Notifications + Notes + Close Case
with right:
    st.markdown("<div class='section-title'>Requests</div>", unsafe_allow_html=True)

    for req in ["🔪 Request Surgery", "🔬 Refer to Specialist", "🧪 Order Lab / Imaging", "💊 Medication Change"]:
        if st.button(req, use_container_width=True, key=req):
            st.session_state["requests"].append(f"{req} — {st.session_state['selected_patient']}")
            st.success(f"Submitted: {req}")

    if st.session_state["requests"]:
        st.markdown("<div class='section-title' style='margin-top:16px;'>Submitted</div>", unsafe_allow_html=True)
        for r in st.session_state["requests"][-3:]:
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #21293a; border-radius:6px;
                        padding:8px 12px; color:#7d8590; font-size:0.75rem; margin-bottom:4px;'>
                📋 {r}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-title' style='margin-top:16px;'>Notifications</div>", unsafe_allow_html=True)
    for n in data["notifications"]:
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:6px;
                    padding:8px 12px; color:#e6edf3; font-size:0.75rem; margin-bottom:6px;'>
            {n['msg']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-title' style='margin-top:16px;'>Clinical Notes</div>", unsafe_allow_html=True)
    if PATIENTS:
        new_notes = st.text_area("", value=PATIENTS[st.session_state["selected_patient"]]["notes"], height=120)
        if st.button("💾 Save Notes", use_container_width=True):
            data["patients"][st.session_state["selected_patient"]]["notes"] = new_notes
            save_data(data)
            st.success("Notes saved!")

    # Close Case
    st.markdown("<div class='section-title' style='margin-top:16px;'>Close Case</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#7d8590; font-size:0.75rem; margin-bottom:8px;'>
        Closing moves the patient to the archive.
    </div>
    """, unsafe_allow_html=True)

    close_reason = st.text_input("", placeholder="Reason e.g. Discharged, Recovered...", key="close_reason")

    if st.button("📁 Close & Archive Case", use_container_width=True, key="close_case"):
        if close_reason.strip() == "":
            st.error("Please provide a reason.")
        else:
            import datetime
            if "archived_patients" not in data:
                data["archived_patients"] = {}
            patient_data = PATIENTS[st.session_state["selected_patient"]].copy()
            patient_data["archived_date"] = datetime.date.today().strftime("%d/%m/%Y")
            patient_data["archive_reason"] = close_reason
            # ← Add these two lines
            patient_data["closed_by"] = st.session_state["name"]
            patient_data["closed_at"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            data["archived_patients"][st.session_state["selected_patient"]] = patient_data
            del data["patients"][st.session_state["selected_patient"]]
            save_data(data)
            st.success(f"{st.session_state['selected_patient']} archived.")
            st.session_state["selected_patient"] = ""
            st.rerun()