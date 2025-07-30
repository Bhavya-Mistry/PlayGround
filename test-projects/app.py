import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# --- USER AUTHENTICATION ---
# Load config file
with open("credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


# --- MAIN APP ---
# Check authentication status
if st.session_state.get("authentication_status"):
    # --- LOGGED-IN VIEW ---
    authenticator.logout('Logout', 'main', key='unique_key_logout')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Your App')
    st.write("This is a protected page.")

else:
    # --- LOGIN/REGISTER VIEW ---
    try:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        # --- LOGIN FORM ---
        with login_tab:
            authenticator.login(location='main')
            if st.session_state["authentication_status"] is False:
                st.error('Username/password is incorrect')
            elif st.session_state["authentication_status"] is None:
                st.warning('Please enter your username and password')

        # --- REGISTRATION FORM ---
        with register_tab:
            if authenticator.register_user(location='main',
                                           fields={'Form name': 'New User Registration'}):
                st.success('User registered successfully! Please go to the Login tab to sign in.')
                # Save the updated credentials back to the file
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)

    except Exception as e:
        st.error(e)