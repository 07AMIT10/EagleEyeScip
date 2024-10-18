import streamlit as st
from google.oauth2 import service_account
from google.cloud import storage
import json

import base64
# import json
# from google.oauth2 import service_account

# In your Streamlit secrets, store the base64 encoded JSON
# credentials_json = base64.b64encode(open('path/to/your/service-account.json', 'rb').read()).decode('utf-8')

# In your code
credentials_json = base64.b64decode(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]).decode('utf-8')
credentials_info = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)

client = storage.Client(credentials=credentials, project=st.secrets["GOOGLE_CLOUD_PROJECT"])

buckets = list(client.list_buckets())
st.write(f"Buckets in project: {', '.join([b.name for b in buckets])}")
