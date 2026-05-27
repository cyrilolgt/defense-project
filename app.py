import streamlit as st
import pickle
import requests
import io

# 1. Define the direct download URL
MODEL_URL = "https://docs.google.com/uc?export=download&confirm=t&id=1K7_pKHGyzW-HLp2FEWwxSwdb4S7P0wMF"

# 2. Cache the download so it only happens once when the app starts up
import os

@st.cache_resource
def load_model_from_drive(url):
    LOCAL_MODEL_PATH = "saved_model.pkl"
    
    # If the file was already downloaded successfully, load it instantly!
    if os.path.exists(LOCAL_MODEL_PATH) and os.path.getsize(LOCAL_MODEL_PATH) > 100000000:
        with open(LOCAL_MODEL_PATH, "rb") as f:
            return pickle.load(f)
            
    # Otherwise, download it once and save it locally
    try:
        with st.spinner("Downloading ML Architecture from Google Drive... Please wait."):
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the raw bytes to the local server disk
            with open(LOCAL_MODEL_PATH, "wb") as f:
                f.write(response.content)
                
        with open(LOCAL_MODEL_PATH, "rb") as f:
            return pickle.load(f)
            
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None
