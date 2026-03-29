import streamlit as st

st.set_page_config(page_title="MediNova Admin Dashboard", layout="wide")

if "name" not in st.session_state or st.session_state["name"] == "":
    st.error("You must log in first")
    st.stop()

from data import load_data, save_data

data = load_data()
PATIENTS = data["patients"]
USERS = data["users"]

# Billing from data.json
if "billing" not in data:
    data["billing"] = {}
BILLING = data["billing"]

# Mock staff data
if "staff" not in st.session_state:
    st.session_state["staff"] = [
        {"name": "Dr. Chris G", "role": "Doctor", "dept": "Orthopaedics", "status": "On Duty"},
        {"name": "Nurse Chris", "role": "Nurse", "dept": "Ward B", "status": "On Duty"},
        {"name": "Dr. Sarah L", "role": "Doctor", "dept": "ICU", "status": "On Call"},
        {"name": "Nurse Jamie", "role": "Nurse", "dept": "Gen-A", "status": "On Break"},
        {"name": "Dr. Ayo O", "role": "Doctor", "dept": "Cardiology", "status": "On Duty"},
    ]

# Bed data
BEDS = {
    "Ortho A": {"total": 12, "occupied": 10},
    "Ortho B": {"total": 10, "occupied": 10},
    "ICU-2":   {"total": 6,  "occupied": 6},
    "Gen-A":   {"total": 16, "occupied": 11},
}

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
    .stSelectbox label { display: none; }
</style>
""", unsafe_allow_html=True)

# Top bar
col_a, col_b = st.columns([6, 1])
with col_a:
    st.markdown(f"""
    <div style='padding:10px 0; border-bottom:1px solid #21293a; margin-bottom:20px;'>
        <span style='font-size:1.4rem; font-weight:700; color:white;'>
            Medi<span style='color:#f0a050;'>Nova</span>
        </span>
        <span style='color:#7d8590; font-size:0.85rem; margin-left:16px;'>{st.session_state['name']}</span>
        <span style='background:rgba(240,160,80,0.1); border:1px solid #f0a050;
                     color:#f0a050; padding:3px 10px; border-radius:20px;
                     font-size:0.75rem; margin-left:8px;'>Admin</span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    if st.button("↩ Logout"):
        st.session_state["name"] = ""
        st.session_state["role"] = ""
        st.switch_page("streamlit.py")

# Stats Row
s1, s2, s3, s4, s5 = st.columns(5)
stats = [
    ("Total Patients", len(PATIENTS), "#f0a050"),
    ("Beds Occupied", sum(b["occupied"] for b in BEDS.values()), "#e05c5c"),
    ("Beds Available", sum(b["total"] - b["occupied"] for b in BEDS.values()), "#3fb8a0"),
    ("Admissions Today", 4, "#7b8ef7"),
    ("Discharges Today", 2, "#f0a050"),
]
for col, (label, value, color) in zip([s1, s2, s3, s4, s5], stats):
    with col:
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-top:2px solid {color};
                    border-radius:8px; padding:14px; text-align:center;'>
            <div style='font-size:0.65rem; color:#4a5568; text-transform:uppercase; letter-spacing:1px;'>{label}</div>
            <div style='font-size:2rem; font-weight:700; color:{color}; margin-top:4px;'>{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

left, middle, right = st.columns([1.5, 3, 1.5])

# LEFT — Bed Management + Staff
with left:
    st.markdown("<div class='section-title'>Bed Occupancy</div>", unsafe_allow_html=True)
    for ward, info in BEDS.items():
        available = info["total"] - info["occupied"]
        pct = int((info["occupied"] / info["total"]) * 100)
        bar_color = "#e05c5c" if pct == 100 else "#f0a050" if pct >= 80 else "#3fb8a0"
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:10px 12px; margin-bottom:8px;'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:white; font-size:0.85rem; font-weight:600;'>{ward}</span>
                <span style='color:{bar_color}; font-size:0.8rem;'>{info["occupied"]}/{info["total"]}</span>
            </div>
            <div style='background:#21293a; border-radius:4px; height:6px; margin-top:6px;'>
                <div style='background:{bar_color}; width:{pct}%; height:6px; border-radius:4px;'></div>
            </div>
            <div style='color:#4a5568; font-size:0.7rem; margin-top:4px;'>{available} bed{"s" if available != 1 else ""} available</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Staff On Duty</div>", unsafe_allow_html=True)
    for s in st.session_state["staff"]:
        status_color = "#3fb8a0" if s["status"] == "On Duty" else "#f0a050" if s["status"] == "On Call" else "#4a5568"
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:10px 12px; margin-bottom:6px;'>
            <div style='color:white; font-size:0.85rem; font-weight:600;'>{s["name"]}</div>
            <div style='display:flex; justify-content:space-between; margin-top:3px;'>
                <span style='color:#7d8590; font-size:0.75rem;'>{s["role"]} · {s["dept"]}</span>
                <span style='color:{status_color}; font-size:0.75rem;'>● {s["status"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# MIDDLE — Patient Admin + Billing
with middle:
    st.markdown("<div class='section-title'>Patient Administration</div>", unsafe_allow_html=True)

    for pname, pdata in PATIENTS.items():
        billing = BILLING.get(pname, {})
        bill_status = billing.get("status", "Unknown")
        bill_color = "#3fb8a0" if bill_status == "Paid" else "#e05c5c" if bill_status == "Overdue" else "#f0a050"
        status = pdata["status"]
        status_color = "#3fb8a0" if status == "Stable" else "#e05c5c" if status == "Critical" else "#f0a050"

        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-radius:8px;
                    padding:14px; margin-bottom:10px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:white; font-size:0.95rem; font-weight:600;'>{pname}</span>
                <span style='color:{status_color}; font-size:0.75rem;'>● {status}</span>
            </div>
            <div style='color:#7d8590; font-size:0.75rem; margin-top:4px;'>
                {pdata["id"]} · {pdata["ward"]} · Insurance: {billing.get("insurance", "Unknown")}
            </div>
            <div style='display:flex; justify-content:space-between; margin-top:8px; align-items:center;'>
                <span style='color:#e6edf3; font-size:0.85rem;'>Invoice: {billing.get("amount", "N/A")}</span>
                <span style='color:{bill_color}; font-size:0.75rem; background:rgba(0,0,0,0.3);
                             border:1px solid {bill_color}; padding:2px 8px; border-radius:4px;'>
                    {bill_status}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Update billing status
    st.markdown("<div class='section-title'>Update Invoice Status</div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([2, 2, 1])
    with b1:
        selected_pt = st.selectbox("", list(PATIENTS.keys()), key="bill_pt")
    with b2:
        new_status = st.selectbox("", ["Pending", "Paid", "Overdue"], key="bill_status")
    with b3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Update", use_container_width=True):
            if selected_pt in data["billing"]:
                data["billing"][selected_pt]["status"] = new_status
                save_data(data)
            st.success(f"{selected_pt} invoice marked as {new_status}")

# RIGHT — Notifications only
with right:
    st.markdown("<div class='section-title'>Notifications</div>", unsafe_allow_html=True)
    admin_notifications = [
        {"color": "#e05c5c", "msg": "Patient Y invoice overdue — 14 days"},
        {"color": "#f0a050", "msg": "Patient X discharge pending approval"},
        {"color": "#3fb8a0", "msg": "Patient Z invoice paid"},
        {"color": "#7b8ef7", "msg": "4 new admissions today"},
    ]
    for n in admin_notifications:
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21293a; border-left:3px solid {n["color"]};
                    border-radius:6px; padding:8px 12px; color:#e6edf3; font-size:0.75rem; margin-bottom:6px;'>
            {n["msg"]}
        </div>
        """, unsafe_allow_html=True)