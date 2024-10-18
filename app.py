import streamlit as st
import openai
import pandas as pd
from PIL import Image
import io
import base64

# Set up OpenAI API key
openai.api_key = "{API key}"

# Initialize session state for product tracking
if 'product_data' not in st.session_state:
    st.session_state.product_data = []

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image(image):
    base64_image = encode_image(image)
    
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image of an FMCG product and provide the following details:"},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}"
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def parse_product_details(analysis):
    details = {
        "Brand Name": "",
        "Date of Manufacturing": "",
        "Date of Expiry": "",
        "Quantity": "",
        "MRP": "",
        "Basic Details": ""
    }
    
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
    
    uploaded_file = st.file_uploader("Choose an image of an FMCG product", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                analysis = analyze_image(image)
                details = parse_product_details(analysis)
                update_product_data(details)
            
            st.subheader("Product Details:")
            for key, value in details.items():
                st.write(f"{key}: {value}")
    
    st.subheader("Product Inventory")
    if st.session_state.product_data:
        df = pd.DataFrame(st.session_state.product_data)
        st.dataframe(df)
    else:
        st.write("No products scanned yet.")

if __name__ == "__main__":
    main()
