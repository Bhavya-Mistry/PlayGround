import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Load config file
with open("credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create authenticator object - use individual parameters, not the whole config
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'], 
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Create login widget - no return values, uses session state instead
try:
    authenticator.login(location='main')
except Exception as e:
    st.error(e)

# Check authentication status from session state
# Check authentication status from session state
if st.session_state.get('authentication_status'):
    # Call the logout method, which will render a logout button
    authenticator.logout('Logout', 'main') 
    st.write(f"Welcome *{st.session_state.get('name')}*")
    st.title("Your App")
    st.write("This is a protected page.")
    
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')        
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')