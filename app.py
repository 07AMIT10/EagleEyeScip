import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import pandas as pd
from PIL import Image
import io
import json
from google.oauth2 import service_account

# Initialize Streamlit page configuration
st.set_page_config(page_title="FMCG Product Analyzer", layout="wide")

# Load Google Cloud credentials
try:
    credentials_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    project_id = st.secrets["GOOGLE_CLOUD_PROJECT"]
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    
    # Initialize the Gemini model
    model = GenerativeModel("gemini-pro-vision")
    st.success("Google Cloud credentials loaded and Gemini model initialized successfully")

    # Debug information
    st.write(f"Project ID: {project_id}")
    st.write("Available models:")
    for available_model in vertexai.generative_models.GenerativeModel.list():
        st.write(available_model.name)

except Exception as e:
    st.error(f"Error loading Google Cloud credentials: {e}")
    st.stop()

# Initialize session state for product tracking
if 'product_data' not in st.session_state:
    st.session_state.product_data = []

def analyze_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    image_part = Part.from_data(img_byte_arr, mime_type="image/png")

    prompt = """
    Analyze this image of an FMCG product and provide the following details:
    - Brand Name
    - Date of Manufacturing
    - Date of Expiry
    - Quantity
    - MRP (Maximum Retail Price)
    - Basic Details (like ingredients or category)

    Present the information in a clear, structured format.
    """

    try:
        response = model.generate_content(
            [image_part, prompt],
            generation_config={
                "max_output_tokens": 1024,
                "temperature": 0.4,
                "top_p": 1,
                "top_k": 32
            }
        )
        return response.text
    except Exception as e:
        st.error(f"Error in image analysis: {e}")
        return None

def parse_product_details(analysis):
    details = {
        "Brand Name": "",
        "Date of Manufacturing": "",
        "Date of Expiry": "",
        "Quantity": "",
        "MRP": "",
        "Basic Details": ""
    }
    
    if analysis:
        lines = analysis.split('\n')
        current_key = None
        for line in lines:
            line = line.strip()
            if line in details:
                current_key = line
            elif current_key and line:
                details[current_key] = line
    
    return details

def update_product_data(details):
    for product in st.session_state.product_data:
        if (product['Brand Name'] == details['Brand Name'] and
            product['Quantity'] == details['Quantity'] and
            product['MRP'] == details['MRP']):
            product['Count'] += 1
            return
    
    details['Count'] = 1
    st.session_state.product_data.append(details)

def main():
    st.title("FMCG Product Analyzer and Tracker")
    
    uploaded_file = st.file_uploader("Choose an image of an FMCG product", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                analysis = analyze_image(image)
                if analysis:
                    details = parse_product_details(analysis)
                    update_product_data(details)
                
                    st.subheader("Product Details:")
                    for key, value in details.items():
                        st.write(f"{key}: {value}")
                else:
                    st.error("Unable to analyze the image. Please try again with a different image.")
    
    st.subheader("Product Inventory")
    if st.session_state.product_data:
        df = pd.DataFrame(st.session_state.product_data)
        st.dataframe(df)
    else:
        st.write("No products scanned yet.")

if __name__ == "__main__":
    main()
