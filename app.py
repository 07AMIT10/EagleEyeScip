import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import pandas as pd
from PIL import Image
import io
import json
from google.oauth2 import service_account
from google.cloud import aiplatform
import re

# [Previous code remains the same up to the analyze_image function]

def analyze_image(image):
    st.write("Starting image analysis...")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    st.write("Image converted to bytes successfully.")

    image_part = Part.from_data(img_byte_arr, mime_type="image/png")
    st.write("Image part created successfully.")

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

    st.write("Sending request to Gemini model...")
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
        st.write("Response received from Gemini model.")
        return response.text
    except Exception as e:
        st.error(f"Error in image analysis: {str(e)}")
        st.write(f"Error type: {type(e).__name__}")
        st.write(f"Error args: {e.args}")
        return None

def parse_product_details(analysis):
    details = {
        "Brand Name": "Not mentioned",
        "Date of Manufacturing": "Not mentioned",
        "Date of Expiry": "Not mentioned",
        "Quantity": "Not mentioned",
        "MRP": "Not mentioned",
        "Basic Details": "Not mentioned"
    }
    
    if analysis:
        # Use regex to extract information
        patterns = {
            "Brand Name": r"\*\*Brand Name:\*\* (.+)",
            "Date of Manufacturing": r"\*\*Date of Manufacturing:\*\* (.+)",
            "Date of Expiry": r"\*\*Date of Expiry:\*\* (.+)",
            "Quantity": r"\*\*Quantity:\*\* (.+)",
            "MRP": r"\*\*MRP:\*\* (.+)",
            "Basic Details": r"\*\*Basic Details:\*\* (.+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, analysis)
            if match:
                details[key] = match.group(1).strip()
    
    return details

# [The rest of the code (update_product_data and main functions) remains the same]

if __name__ == "__main__":
    main()
