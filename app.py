import streamlit as st
import pandas as pd
import joblib
import os

# Load trained model
model_path = os.path.join(os.path.dirname(__file__), "diabetes_model.pkl")
model = joblib.load(model_path)

# UI Header
st.set_page_config(page_title="Diabetes Prediction App", layout="wide")
st.markdown("""
    <style>
        .main {background-color: #f9f9f9; padding: 20px;}
        .stButton>button {background-color: #007BFF; color: white; font-size: 16px; padding: 10px 20px; border-radius: 5px;}
        .stTextInput, .stNumberInput, .stSelectbox, .stRadio, .stSlider {margin-bottom: 15px;}
        h1, h2, h3, h4, h5, h6 {font-weight: bold;}
        h1 {font-size: 3rem;}
        h2 {font-size: 2.5rem;}
        h3 {font-size: 2rem;}
        .section-heading {font-size: 1.75rem; font-weight: bold; margin-top: 20px; margin-bottom: 10px;}
        .streamlit-expanderHeader {font-size: 1.5rem; font-weight: bold;} /* Custom font size for expander titles */
    </style>
""", unsafe_allow_html=True)

st.title("🩺 Diabetes Prediction App")
st.write("This app predicts the likelihood of diabetes based on your health details. Please fill in the information below.")

st.markdown("---")

# Input form
def user_input():
    st.header("**User Input Features**")
    st.write("Please provide the following information:")

    # Organize inputs into collapsible sections
    data = {}

    with st.expander("General Information", expanded=True):
        data["Age"] = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1, key="age")
        data["BMI"] = st.number_input("Body Mass Index (BMI)", min_value=10.0, max_value=50.0, value=25.0, key="bmi")
        data["Sex"] = st.selectbox("Gender", ["Male", "Female"], key="sex")

    with st.expander("Health Conditions", expanded=False):
        fields = {
            "HighBP": "High Blood Pressure",
            "HighChol": "High Cholesterol",
            "CholCheck": "Cholesterol Check in the Last 5 Years",
            "Smoker": "Smoker",
            "Stroke": "History of Stroke",
            "HeartDiseaseorAttack": "Heart Disease or Heart Attack",
            "PhysActivity": "Physically Active",
            "Fruits": "Consumes Fruits Regularly",
            "Veggies": "Consumes Vegetables Regularly",
            "HvyAlcoholConsump": "Heavy Alcohol Consumption",
            "AnyHealthcare": "Has Access to Healthcare",
            "NoDocbcCost": "Could Not See Doctor Due to Cost",
            "DiffWalk": "Difficulty Walking",
        }
        cols = st.columns(2)  # Split into 2 columns
        for i, (field, label) in enumerate(fields.items()):
            col = cols[i % 2]
            data[field] = col.radio(label, ["Yes", "No"], index=1, key=field)

    with st.expander("Health Ratings", expanded=False):
        data["GenHlth"] = st.slider("General Health (1=Excellent, 5=Poor)", 1, 5, value=3, key="genhlth")
        data["MentHlth"] = st.slider("Mental Health Issues (days/month)", 0, 30, value=5, key="menthlth")
        data["PhysHlth"] = st.slider("Physical Health Issues (days/month)", 0, 30, value=5, key="physhlth")

    # Ensure the order of features matches the trained model
    feature_order = ["HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", "HeartDiseaseorAttack", 
                     "PhysActivity", "Fruits", "Veggies", "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", 
                     "GenHlth", "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age"]

    # Convert categorical inputs to numeric
    data["Sex"] = 1 if data["Sex"] == "Male" else 0
    for field in fields.keys():
        data[field] = 1 if data[field] == "Yes" else 0

    return pd.DataFrame([[data[feature] for feature in feature_order]], columns=feature_order)

# Get user input
input_df = user_input()

# Predict button
if input_df is not None:
    st.markdown("---")
    st.subheader("**Prediction Results**")
    
    # Use plain text for the button label
    if st.button("🔍 Predict Diabetes"):
        with st.spinner("Analyzing your data..."):
            prediction = model.predict(input_df)[0]
            
            # Customize the output based on the prediction
            if prediction == 1:  # Diabetic
                st.markdown(
                    """
                    <div style="text-align: center; padding: 20px; background-color: #ffcccc; border-radius: 10px;">
                        <img src="https://img.icons8.com/ios-filled/100/fa314a/error.png" width="50" style="margin-bottom: 10px;">
                        <h2 style="color: #d9534f;"><b>Diabetic</b></h2>
                        <p style="font-size: 18px;">Based on the information provided, the model predicts that you are at risk of diabetes.</p>
                        <p style="font-size: 16px;">Please consult a healthcare professional for further advice and diagnosis.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:  # Non-Diabetic
                st.markdown(
                    """
                    <div style="text-align: center; padding: 20px; background-color: #d4edda; border-radius: 10px;">
                        <img src="https://img.icons8.com/ios-filled/100/28a745/checked.png" width="50" style="margin-bottom: 10px;">
                        <h2 style="color: #28a745;"><b>Non-Diabetic</b></h2>
                        <p style="font-size: 18px;">Based on the information provided, the model predicts that you are not at risk of diabetes.</p>
                        <p style="font-size: 16px;">Maintain a healthy lifestyle and consult a healthcare professional for regular checkups.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Add disclaimer about model limitations
            st.markdown(
                """
                <div style="text-align: center; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #ddd;">
                    <p style="font-size: 14px; color: #6c757d;">
                        <i>Disclaimer: This prediction is based on a machine learning model trained on a small dataset. 
                        The results may vary and could be subject to biases or inaccuracies. Please consult a healthcare professional for a comprehensive diagnosis.</i>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Add a professional footer
st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f9f9f9;
            padding: 10px 20px;
            text-align: center;
            font-size: 14px;
            color: #6c757d;
            border-top: 1px solid #eaeaea;
        }
        .footer a {
            color: #007BFF;
            text-decoration: none;
            font-weight: bold;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        Connect with me on 
        <a href="https://www.linkedin.com/in/manvendrapratapsinghdev/" target="_blank">LinkedIn</a>.
    </div>
    """,
    unsafe_allow_html=True
)
