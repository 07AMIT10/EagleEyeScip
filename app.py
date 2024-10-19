import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import pandas as pd
from PIL import Image
import io
import json
from google.oauth2 import service_account

# ... (previous code remains the same)

# Initialize Vertex AI
vertexai.init(project=project_id, location="us-central1", credentials=credentials)

# Initialize the Gemini model
model = GenerativeModel("gemini-pro-vision")
st.success("Google Cloud credentials loaded and Gemini model initialized successfully")


st.write(f"Project ID: {project_id}")
st.write(f"Available models:")
for model in vertexai.generative_models.GenerativeModel.list():
    st.write(model.name)



# ... (rest of the code remains the same)





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

# ... (rest of the code remains the same)
