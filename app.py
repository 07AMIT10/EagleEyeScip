import streamlit as st
from google.oauth2 import service_account
from google.cloud import storage
import json

credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
)

client = storage.Client(credentials=credentials, project=st.secrets["GOOGLE_CLOUD_PROJECT"])

buckets = list(client.list_buckets())
st.write(f"Buckets in project: {', '.join([b.name for b in buckets])}")
