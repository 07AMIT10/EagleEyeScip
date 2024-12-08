import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import pandas as pd
from PIL import Image
import io
import json
import re
from google.oauth2 import service_account
from google.cloud import aiplatform

# Initialize Streamlit page configuration
st.set_page_config(page_title="FMCG Product Analyzer", layout="wide")

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .viewerBadge_container__1QSob {visibility: hidden;}
        .css-1lsmgbg.egzxvld1 {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load Google Cloud credentials
try:
    credentials_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    project_id = st.secrets["GOOGLE_CLOUD_PROJECT"]
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    
    # Initialize the Gemini model
    model = GenerativeModel("gemini-1.5-flash-002")
    st.success("Model loaded successfully")

except Exception as e:
    st.error(f"Error loading Google Cloud credentials: {str(e)}")
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
    1. Brand Name
    2. Date of Manufacturing (format: MM/YYYY)
    3. Date of Expiry (format: MM/YYYY). If 'Best Before' is given, calculate the expiry date and provide only the final date.
    4. Quantity (provide only the numerical value and unit, e.g., 400 ml)
    5. MRP (Maximum Retail Price) (provide only the numerical value with currency symbol, e.g., ₹400)
    6. Basic Details (like ingredients or category)

    Present the information in a clear, structured format without additional explanations.
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
        st.error(f"Error in image analysis: {str(e)}")
        return None

def parse_product_details(analysis):
    details = {
        "Brand Name": "Not identified",
        "Date of Manufacturing": "Not specified",
        "Date of Expiry": "Not specified",
        "Quantity": "Not specified",
        "MRP": "Not specified",
        "Basic Details": "Not provided"
    }
    
    if analysis:
        lines = analysis.split('\n')
        current_key = None
        for line in lines:
            line = line.strip()
            if line.startswith('1.') and 'Brand Name:' in line:
                current_key = "Brand Name"
                details[current_key] = line.split(':', 1)[1].strip()
            elif line.startswith('2.') and 'Date of Manufacturing:' in line:
                current_key = "Date of Manufacturing"
                details[current_key] = line.split(':', 1)[1].strip()
            elif line.startswith('3.') and 'Date of Expiry:' in line:
                current_key = "Date of Expiry"
                details[current_key] = line.split(':', 1)[1].strip()
            elif line.startswith('4.') and 'Quantity:' in line:
                current_key = "Quantity"
                details[current_key] = line.split(':', 1)[1].strip()
            elif line.startswith('5.') and 'MRP:' in line:
                current_key = "MRP"
                details[current_key] = line.split(':', 1)[1].strip()
            elif line.startswith('6.') and 'Basic Details:' in line:
                current_key = "Basic Details"
                details[current_key] = line.split(':', 1)[1].strip()
            elif current_key == "Basic Details":
                details[current_key] += " " + line
    
    return details

def update_product_data(details):
    # Check if product already exists
    for product in st.session_state.product_data:
        if (product['Brand Name'].lower() == details['Brand Name'].lower() and
            product['Quantity'] == details['Quantity'] and
            product['MRP'] == details['MRP']):
            # Update existing entry
            product['Count'] += 1
            return
    
    # Add new entry if not found
    details['Count'] = 1
    st.session_state.product_data.append(details)

def main():
    st.title("FMCG Product Analyzer and Tracker")
    
    uploaded_file = st.file_uploader("Choose an image of an FMCG product", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Resize image for display
        max_width = 300
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        resized_image = image.resize(new_size)
        
        # Display resized image
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(resized_image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("Analyze Image"):
                with st.spinner("Analyzing image..."):
                    analysis = analyze_image(image)
                    if analysis:
                        details = parse_product_details(analysis)
                        update_product_data(details)
                    
                        st.subheader("Product Details:")
                        for key, value in details.items():
                            if key != 'Count':
                                st.write(f"**{key}:** {value}")
                    else:
                        st.error("Unable to analyze the image. Please try again with a different image.")
    
    st.subheader("Product Inventory")
    if st.session_state.product_data:
        df = pd.DataFrame(st.session_state.product_data)
        
        # Reorder columns
        columns_order = ['Brand Name', 'Date of Manufacturing', 'Date of Expiry', 'Quantity', 'MRP', 'Basic Details', 'Count']
        df = df[columns_order]
        
        # Style the dataframe
        styled_df = df.style.set_properties(**{'text-align': 'left'})
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'left')]},
            {'selector': 'td', 'props': [('max-width', '200px'), ('white-space', 'normal')]}
        ])
        
        st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("No products scanned yet.")

if __name__ == "__main__":
    main()
