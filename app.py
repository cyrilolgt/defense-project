import streamlit as st
import joblib
import os

# 1. The local file path inside your project folder
LOCAL_MODEL_PATH = "saved_model.joblib"

@st.cache_resource
def load_model_locally():
    if os.path.exists(LOCAL_MODEL_PATH):
        try:
            return joblib.load(LOCAL_MODEL_PATH)
        except Exception as e:
            st.error(f"Error loading model file: {e}")
            return None
    else:
        st.error(f"Model file '{LOCAL_MODEL_PATH}' not found!")
        return None

# 2. Load the model instantly from your local repo files
model = load_model_locally()

# =========================================================
# YOUR ORIGINAL CODE (LINES 24-40) STARTS RIGHT HERE:
# =========================================================
st.title("🌾 CropCast Global Dashboard")
# ... your inputs, sliders, and prediction logic continue here ...
                    if chunk:
                        f.write(chunk)
                        
        return joblib.load(LOCAL_MODEL_PATH)
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        return None

# Load the model safely
model = load_model_from_drive(MODEL_URL)

# --- Your remaining Streamlit UI / Prediction code goes here ---
st.title("🌾 CropCast Global Dashboard")
if model is not None:
    st.success("Predictive engine successfully loaded and cached!")

