

import streamlit as st
from utils.api_client import APIClient
from utils.s3_client import S3Client

API_URL = "http://127.0.0.1:8000"
client = APIClient(API_URL)
s3_client = S3Client()

st.set_page_config(page_title="Diagnosis", layout="centered")
st.title("🩺 Aicenna Diagnosis Platform")

st.markdown("Upload an image, choose **disease** and **model**, then run inference.")

disease = st.selectbox("Select disease", ["chest", "brain", "alzheimer"])

if disease == "chest":
    model_choice = st.selectbox("Select chest model", ["tf_efficientnetv2_b0", "swin_tiny_patch4_window7_224", "best_chest_xray_model.h5"])
elif disease == "brain":
    model_choice = st.selectbox("Select brain model", ["brain_best.pt"])
else:
    model_choice = st.selectbox("Select Alzheimer model", ["alz_best.pt", "alzheimer_model.keras"])

uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

if st.button("Run Inference"):
    if uploaded_file is None:
        st.warning("Please upload an image file first.")
    else:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        # 🔹 Step 1: Upload to MinIO
        s3_path = s3_client.upload_file(file_bytes, file_name)
        #st.info(f"✅ Uploaded to MinIO: {s3_path}")

        # 🔹 Step 2: Download from MinIO into ./images
        local_path = s3_client.download_file(file_name, "images")
        #st.info(f"📥 Downloaded locally to: {local_path}")

        # 🔹 Step 3: Run inference (same as current implementation)
        file_tuple = (uploaded_file.name, file_bytes, uploaded_file.type)

        with st.spinner("Running inference..."):
            try:
                resp = client.predict_image(disease, model_choice, file_tuple)
                result = resp.get("result", "Error")
                pred_class = resp.get("predicted_class", "Unknown")
                conf = resp.get("confidence", 0.0)

                if result == "Yes":
                    st.success("Prediction: YES (disease detected)")
                elif result == "No":
                    st.success("Prediction: NO (normal)")
                else:
                    st.error(f"Prediction failed: {result}")

                st.caption(f"Predicted class: {pred_class} — Confidence: {conf:.2f}")

            except Exception as e:
                st.error(f"Backend request failed: {e}")


