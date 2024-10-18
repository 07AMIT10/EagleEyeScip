import streamlit as st
import json
from google.oauth2 import service_account

# Safely check if the secret exists
if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
    try:
        credentials_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        st.success("Credentials loaded successfully")
    except json.JSONDecodeError:
        st.error("Error decoding JSON from secret")
else:
    st.error("GOOGLE_APPLICATION_CREDENTIALS secret not found")

# Rest of your app code here
