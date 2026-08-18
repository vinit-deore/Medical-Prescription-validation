import streamlit as st

DEMO_USERS = {
    "dr_fleming": {
        "username": "dr_fleming",
        "name": "Dr. Alexander Fleming",
        "role": "Senior Cardiologist",
        "department": "Cardiovascular Medicine",
        "avatar": "👨‍⚕️",
        "password": "demo"
    },
    "dr_blackwell": {
        "username": "dr_blackwell",
        "name": "Dr. Elizabeth Blackwell",
        "role": "Lead Clinical Pharmacist",
        "department": "Pharmacy Services",
        "avatar": "👩‍⚕️",
        "password": "demo"
    },
    "dr_house": {
        "username": "dr_house",
        "name": "Dr. Gregory House",
        "role": "Head of Diagnostic Medicine",
        "department": "Internal Medicine",
        "avatar": "🩺",
        "password": "demo"
    }
}

def login_user(username, password=None, is_demo=False):
    """Logs in a clinician and updates session state."""
    username_clean = username.strip().lower()
    if is_demo and username_clean in DEMO_USERS:
        st.session_state.authenticated = True
        st.session_state.current_user = DEMO_USERS[username_clean]
        return True, "Login successful."

    if username_clean in DEMO_USERS:
        if password == DEMO_USERS[username_clean]["password"] or password == "demo123" or is_demo:
            st.session_state.authenticated = True
            st.session_state.current_user = DEMO_USERS[username_clean]
            return True, "Login successful."

    # Default fallback login for custom username
    st.session_state.authenticated = True
    st.session_state.current_user = {
        "username": username_clean,
        "name": f"Dr. {username_clean.title()}",
        "role": "Attending Physician",
        "department": "Central Clinical Care",
        "avatar": "👨‍⚕️"
    }
    return True, "Login successful."

def logout_user():
    """Logs out current user."""
    st.session_state.authenticated = False
    st.session_state.current_user = None

def is_authenticated():
    """Returns True if user is logged in."""
    return st.session_state.get("authenticated", False)
