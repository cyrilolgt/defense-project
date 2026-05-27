import streamlit as st
import pickle
import requests
import io

# 1. Define the direct download URL
MODEL_URL = 'https://drive.google.com/uc?export=download&id=1K7_pKHGyzW-HLp2FEWwxSwdb4S7P0wMF'

# 2. Cache the download so it only happens once when the app starts up
@st.cache_resource
def load_model_from_drive(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        model = pickle.load(io.BytesIO(response.content))
        return model
    except Exception as e:
        st.error(f'Error loading model from Google Drive: {e}')
        return None

# 3. Load the model
model = load_model_from_drive(MODEL_URL)
