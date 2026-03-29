import streamlit as st
import sys
import os

# Initialize session_state for selected patients
if "selected_patients" not in st.session_state:
    st.session_state["selected_patients"] = []


st.set_page_config(page_title="Patient Staff Assignment", layout="wide")

#if "name" not in st.session_state or st.session_state["name"] == "":
#    st.error("You must log in first")
#    st.stop()

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(".."))  # ".." is the parent folder

from data import load_data, save_data
data = load_data()

PATIENTS = data["patients"]
USERS = data["users"]

st.markdown("""
<style>
    .stApp {background-color: #0d1117; color: #e6edf3;}
            
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
  
    .section-title {
        font-zise: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #4a5568;
        border-bottom: 6px;
        margin-bottom: 10px; 

    }
</style>
""", unsafe_allow_html=True)

col_a, col_b = st.columns([6, 1])
with col_a:
    st.markdown("""
    <div style='padding:10px 0; border-bottom:1px solid #21293a; margin-bottom:20px;'>
        <span style='font-size:1.4rem; font-weight:700; color:white;'>
            Medi<span style='color:#3fb8a0;'>Nova</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    if st.button("↩ Logout"):
        st.session_state["name"] = ""
        st.session_state["role"] = ""
        st.switch_page("Streamlit.py")

# Initialize session state
if "selected_staff" not in st.session_state:
    st.session_state["selected_staff"] = list(USERS.keys())[0]
if "staff_assignments" not in st.session_state:
    # Example: store which patients are assigned to which staff
    st.session_state["staff_assignments"] = {sname: [] for sname in USERS.keys()}

# Main layout: left column for staff, right column for patients
padding_left, left, right, padding_right = st.columns([2, 2, 2, 1])

# ----- LEFT: Staff selection buttons -----
with left:
    st.markdown("## Staff")
    st.markdown("Select a staff member to assign patients.")
    for sname in USERS.keys():
        if st.session_state["selected_staff"] == sname:
            # Display as a red “button” using markdown
            st.markdown(
            f"""
            <div style="
                display:inline-block;
                background-color:#ff4b4b;
                color:white;
                padding:8px 20px;
                text-align:center;
                margin-bottom:10px;
                border-radius:5px;
                font-weight:bold;
                cursor: default;
            ">
                {sname}
            </div>
            """,
            unsafe_allow_html=True
        )
        else:
            if st.button(sname):
                st.session_state["selected_staff"] = sname
                st.rerun()  # refresh to highlight new selection

# ----- RIGHT: split into upper and lower sections -----
with right:
    if st.session_state["selected_staff"]:
        staff = st.session_state["selected_staff"]
        assigned = st.session_state["staff_assignments"][staff]

        # Split right column into upper and lower containers using st.container
        upper_right = st.container()
        lower_right = st.container()

        # Upper-right: assigned patients
        with upper_right:
            st.markdown("### Assigned Patients")
            if assigned:
                for pname in assigned:
                    st.markdown(f"- {pname}")
            else:
                st.markdown("No patients assigned yet.")

        # Lower-right: unassigned patients
        with lower_right:
            st.markdown("### Unassigned Patients")

            # Temp selection storage (per staff)
            temp_key = f"temp_selected_{staff}"
            if temp_key not in st.session_state:
                st.session_state[temp_key] = []

            temp_selected = st.session_state[temp_key]

            # Show checkboxes
            for pname in PATIENTS.keys():
                if pname not in assigned:
                    checked = st.checkbox(
                        pname,
                        key=f"assign_{staff}_{pname}",
                        value=pname in temp_selected
                    )

                    if checked and pname not in temp_selected:
                        temp_selected.append(pname)
                    elif not checked and pname in temp_selected:
                        temp_selected.remove(pname)

            # Password input
            password = st.text_input("Enter password to confirm", type="password")

            # Save button
            if st.button("Save Assignments"):
                if password == "admin123":  # 🔒 change this to your real logic
                    for pname in temp_selected:
                        if pname not in assigned:
                            st.session_state["staff_assignments"][staff].append(pname)

                    # Clear temp selections
                    st.session_state[temp_key] = []

                    st.success("Assignments saved successfully!")
                    st.rerun()
                else:
                    st.error("Incorrect password. Changes not saved.")

            # Back button directly under Save Assignments
            role = st.session_state.get("role", "")

            # Define a mapping of roles → pages
            role_pages = {
                "admin": "AdminDashboard",
                "nurse": "NurseDashboard",
                "doctor": "DoctorDashboard"
                # add other roles and pages as needed
            }

            back_page = role_pages.get(role)  # fallback page

            if st.button("← Back"):
                st.switch_page(back_page)