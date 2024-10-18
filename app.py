import streamlit as st
import os
from openai import OpenAI
import pandas as pd
from PIL import Image
import io
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state for product tracking
if 'product_data' not in st.session_state:
    st.session_state.product_data = []

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image(image):
    base64_image = encode_image(image)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image of an FMCG product and provide the following details: Brand Name, Date of Manufacturing, Date of Expiry, Quantity, MRP, and Basic Details (like ingredients or category)."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"  # Using high detail for better analysis
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred during image analysis: {str(e)}")
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
        for line in lines:
            for key in details.keys():
                if key in line:
                    details[key] = line.split(':')[-1].strip()
    
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
    
    uploaded_file = st.file_uploader("Choose an image of an FMCG product", type=["jpg", "jpeg", "png", "webp", "gif"])
    
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
