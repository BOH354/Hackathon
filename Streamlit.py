import streamlit as st
import hashlib

st.set_page_config(page_title="MedNova", layout="centered")

# Mock Database
USERS = {
    "Dr. Chris G": {"password": "9cb5f3995e866211201b10c9e7a7e7c1c1a4105d1a6113fc4d920cc060ff114bb4b1fab3c7bf7892d47b2d26ddbebbdf9c1502fc32991708739d272789703d2c", "role": "Doctor"},
    "Nurse Chris": {"password": "8c744d2514340f39fcb487bacaa5d958aac0f922aa35837ef6a7ba1bcf6eb429c8adfc0b0bc1075208b456a66fb636631aff9b9fc2679db6c5c103e54ba6052a", "role": "Nurse"},
    "Admin Chris": {"password": "69d5375dfb20ed2faf39b27301c64630905ebc08bcaa1d603b3d6c2139613319bf3559ca999930f2e280f0e3d236a4ca9fb87ce0579ff730f6612b897c7b0aca", "role": "Admin"},
    "ChargeNurse Chris": {"password": "7a8c022c4fecdfce5e31c54ffc3e825c52284b90740fd1eeb024bf2846c9ba88c4c0b796ed8cb5bb5e44b03b34d88880c1b63f28dc7689d280655a1fcd984d4d", "role": "ChargeNurse"},
}

if "role" not in st.session_state:
    st.session_state["role"] = "Doctor"
if "name" not in st.session_state:
    st.session_state["name"] = ""
if "redirect_to_archive" not in st.session_state:
    st.session_state["redirect_to_archive"] = False

# CSS
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    a[href] { display: none !important; }
    .block-container { padding-top: 8vh !important; }
    .stTextInput input {
        background-color: #1c2330 !important;
        border: 1px solid #21293a !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    .stButton button {
        background-color: #3fb8a0;
        color: #0d1117;
        font-weight: 600;
        width: 100%;
        border: none;
        border-radius: 8px;
        letter-spacing: 1px;
        font-size: 0.7rem !important;
        padding: 8px 4px !important;
        height: 42px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .stButton button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.5, 4, 0.5])

with col2:
    # Logo
    st.markdown("""
    <div style='text-align:center; margin-bottom:8px;'>
        <span style='font-size:2.5rem; font-weight:700; color:white;'>Med</span>
        <span style='font-size:2.5rem; font-weight:700; color:#3fb8a0;'>Nova</span>
    </div>
    <div style='text-align:center; color:#4a5568; font-size:0.8rem;
                letter-spacing:2px; text-transform:uppercase; margin-bottom:32px;'>
        Secure Hospital Management
    </div>
    """, unsafe_allow_html=True)

    # Archive banner
    if st.session_state.get("redirect_to_archive"):
        st.markdown("""
        <div style='background:rgba(123,142,247,0.1); border:1px solid #7b8ef7;
                    border-radius:8px; padding:10px 16px; color:#7b8ef7;
                    font-size:0.85rem; margin-bottom:12px;'>
            📁 Please log in as a Doctor or Charge Nurse to access the Archive.
        </div>
        """, unsafe_allow_html=True)

    # Login card
    with st.container(border=True):
        st.markdown("<p style='color:#7d8590; margin-bottom:4px;'>Select your role</p>", unsafe_allow_html=True)

        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            if st.button("🩺 Doctor", use_container_width=True):
                st.session_state["role"] = "Doctor"
                st.session_state["redirect_to_archive"] = False
        with r2:
            if st.button("💊 Nurse", use_container_width=True):
                st.session_state["role"] = "Nurse"
                st.session_state["redirect_to_archive"] = False
        with r3:
            if st.button("🗂️ Admin", use_container_width=True):
                st.session_state["role"] = "Admin"
                st.session_state["redirect_to_archive"] = False
        with r4:
            if st.button("🏥 CN", use_container_width=True):
                st.session_state["role"] = "ChargeNurse"
                st.session_state["redirect_to_archive"] = False
        with r5:
            if st.button("📁 Archive", use_container_width=True):
                st.session_state["redirect_to_archive"] = True
                st.rerun()

        if st.session_state["role"] == "Doctor":
            default_name = "Dr. "
        elif st.session_state["role"] == "Nurse":
            default_name = "Nurse "
        elif st.session_state["role"] == "ChargeNurse":
            default_name = "ChargeNurse "
        else:
            default_name = ""

        name = st.text_input("", value=default_name, placeholder="Full name (e.g. Dr. Chris G)").strip()
        password = st.text_input("", placeholder="Password", type="password")

        if st.button("ACCESS DASHBOARD →", use_container_width=True):
            if name in USERS:
                hash_from_db = bytes.fromhex(USERS[name]["password"])
                salt_from_db = hash_from_db[:32]
                key_from_db = hash_from_db[32:]
                temp_key = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt_from_db, 100000)
                if temp_key == key_from_db:
                    actual_role = USERS[name]["role"]
                    selected_role = st.session_state["role"]

                    # Archive redirect — allow Doctor and ChargeNurse
                    if st.session_state.get("redirect_to_archive"):
                        if actual_role not in ["Doctor", "ChargeNurse"]:
                            st.error("Access denied. Only Doctors and Charge Nurses can access the Archive.")
                        else:
                            st.session_state["name"] = name
                            st.session_state["role"] = actual_role
                            st.session_state["redirect_to_archive"] = False
                            st.success(f"Welcome, {name}!")
                            st.switch_page("pages/Archive.py")

                    # Normal login
                    elif actual_role != selected_role:
                        st.error(f"Access denied. Your account is registered as {actual_role}, not {selected_role}.")
                    else:
                        st.session_state["name"] = name
                        st.session_state["role"] = actual_role
                        st.success(f"Welcome, {name}!")
                        if actual_role == "Doctor":
                            st.switch_page("pages/DoctorDashBoard.py")
                        elif actual_role == "Nurse":
                            st.switch_page("pages/NurseDashBoard.py")
                        elif actual_role == "Admin":
                            st.switch_page("pages/AdminDashBoard.py")
                        elif actual_role == "ChargeNurse":
                            st.switch_page("pages/PaitentManagmentDashBoard.py")
                else:
                    st.error("Invalid name or password. Access denied.")
            else:
                st.error("Invalid name or password. Access denied.")

    # Footer
    st.markdown("""
    <div style='text-align:center; color:#21293a; font-size:0.75rem; margin-top:24px;'>
        © 2026 MediNova · Authorised Personnel Only
    </div>
    """, unsafe_allow_html=True)