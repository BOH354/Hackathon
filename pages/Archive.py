import streamlit as st
import datetime
from data import load_data, save_data

st.set_page_config(page_title="MediNova Archive", layout="wide")

# Login check
if "name" not in st.session_state or st.session_state["name"] == "":
    st.error("You must log in first")
    st.stop()

# Role check
allowed_roles = ["Doctor", "ChargeNurse"]
if st.session_state["role"] not in allowed_roles:
    st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #e6edf3; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex; flex-direction:column; align-items:center; justify-content:center;
                padding:80px 20px; text-align:center;'>
        <div style='font-size:3rem; margin-bottom:16px;'>🔒</div>
        <div style='font-size:1.5rem; font-weight:700; color:white; margin-bottom:8px;'>Access Restricted</div>
        <div style='color:#7d8590; font-size:0.9rem; max-width:400px; line-height:1.6;'>
            The Archive is only accessible to Doctors and Charge Nurses.
            Your current role <span style='color:#e05c5c;'>({role})</span> does not have permission.
        </div>
    </div>
    """.format(role=st.session_state["role"]), unsafe_allow_html=True)
    if st.button("↩ Go Back"):
        if st.session_state["role"] == "Nurse":
            st.switch_page("pages/NurseDashBoard.py")
        elif st.session_state["role"] == "Admin":
            st.switch_page("pages/AdminDashBoard.py")
        else:
            st.switch_page("streamlit.py")
    st.stop()

# Load data
data = load_data()

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
                     font-size:0.75rem; margin-left:8px;'>{st.session_state['role']}</span>
        <span style='background:rgba(123,142,247,0.1); border:1px solid #7b8ef7;
                     color:#7b8ef7; padding:3px 10px; border-radius:20px;
                     font-size:0.75rem; margin-left:8px;'>📁 Archive</span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    if st.button("↩ Back"):
        if st.session_state["role"] == "Doctor":
            st.switch_page("pages/DoctorDashBoard.py")
        else:
            st.switch_page("pages/PaitentManagmentDashBoard.py")

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1, 2])

# LEFT — Archived patient list
with left:
    st.markdown("<div class='section-title'>Archived Patients</div>", unsafe_allow_html=True)

    if "archived_patients" not in data or not data["archived_patients"]:
        st.markdown("""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:16px; color:#4a5568; font-size:0.85rem; text-align:center;'>
            No archived patients yet.
        </div>
        """, unsafe_allow_html=True)
    else:
        for pname, pdata in data["archived_patients"].items():
            status = pdata.get("status", "Unknown")
            color = '#3fb8a0' if status == "Stable" else '#e05c5c' if status == "Critical" else '#f0a050'
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                        padding:12px; margin-bottom:8px;'>
                <div style='color:white; font-size:0.9rem; font-weight:600;'>{pname}</div>
                <div style='color:#7d8590; font-size:0.75rem;'>{pdata.get("condition", "N/A")}</div>
                <div style='color:{color}; font-size:0.75rem; margin-top:4px;'>
                    ● {status} · {pdata.get("ward", "N/A")}
                </div>
                <div style='color:#4a5568; font-size:0.7rem; margin-top:4px;'>
                    Archived: {pdata.get("archived_date", "Unknown date")}
                </div>
                <div style='color:#3fb8a0; font-size:0.7rem; margin-top:2px;'>
                    ⚕️ {pdata.get("closed_by", "Unknown")}
                </div>
            </div>
            """, unsafe_allow_html=True)

# RIGHT — View archived record only
with right:
    st.markdown("<div class='section-title'>View Archived Record</div>", unsafe_allow_html=True)

    if "archived_patients" not in data or not data["archived_patients"]:
        st.markdown("""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:24px; text-align:center; color:#4a5568; font-size:0.85rem;'>
            No archived records to view yet.<br>
            <span style='font-size:0.75rem;'>Cases can only be closed from the Doctor Dashboard.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        view_patient = st.selectbox("", list(data["archived_patients"].keys()), key="view_archive")
        ap = data["archived_patients"][view_patient]

        # Log view
        if "viewed_by" not in data["archived_patients"][view_patient]:
            data["archived_patients"][view_patient]["viewed_by"] = []
        view_entry = f"{st.session_state['name']} — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        if not data["archived_patients"][view_patient]["viewed_by"] or \
           data["archived_patients"][view_patient]["viewed_by"][-1].split(" —")[0] != st.session_state['name']:
            data["archived_patients"][view_patient]["viewed_by"].append(view_entry)
            save_data(data)

        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px; padding:16px;'>
            <div style='color:white; font-size:1rem; font-weight:700; margin-bottom:8px;'>{view_patient}</div>
            <div style='color:#7d8590; font-size:0.8rem;'>{ap.get("id", "N/A")} · {ap.get("ward", "N/A")}</div>
            <div style='color:#e6edf3; font-size:0.85rem; margin-top:8px;'><b>Diagnosis:</b> {ap.get("diagnosis", "N/A")}</div>
            <div style='color:#e6edf3; font-size:0.85rem; margin-top:4px;'><b>Allergies:</b> {ap.get("allergies", "N/A")}</div>
            <div style='color:#e6edf3; font-size:0.85rem; margin-top:4px;'><b>Archive Reason:</b> {ap.get("archive_reason", "N/A")}</div>
            <div style='color:#4a5568; font-size:0.75rem; margin-top:8px;'>Archived: {ap.get("archived_date", "N/A")}</div>
            <div style='background:rgba(63,184,160,0.08); border:1px solid rgba(63,184,160,0.2);
                        border-radius:6px; padding:8px 12px; margin-top:12px;
                        display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#3fb8a0; font-size:0.8rem;'>⚕️ Closed by {ap.get("closed_by", "Unknown")}</span>
                <span style='color:#4a5568; font-size:0.75rem;'>{ap.get("closed_at", "Unknown date")}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Current viewer tag
        st.markdown(f"""
        <div style='background:rgba(123,142,247,0.06); border:1px solid rgba(123,142,247,0.2);
                    border-radius:6px; padding:8px 12px; margin-top:8px;
                    display:flex; justify-content:space-between; align-items:center;'>
            <span style='color:#7b8ef7; font-size:0.8rem;'>👁️ Viewed by {st.session_state['name']}</span>
            <span style='color:#4a5568; font-size:0.75rem;'>{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
        """, unsafe_allow_html=True)

        # View history
        if ap.get("viewed_by"):
            st.markdown("<div class='section-title' style='margin-top:16px;'>View History</div>", unsafe_allow_html=True)
            for entry in ap["viewed_by"][-5:]:
                st.markdown(f"""
                <div style='color:#4a5568; font-size:0.75rem; padding:4px 0; border-bottom:1px solid #21293a;'>
                    👁️ {entry}
                </div>
                """, unsafe_allow_html=True)