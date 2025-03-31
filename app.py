import streamlit as st
import pandas as pd
import joblib
import os
import json
import threading

# Load trained model
model_path = os.path.join(os.path.dirname(__file__), "diabetes_model.pkl")
model = joblib.load(model_path)

# Load translations from the JSON file
with open("translations.json", "r") as file:
    translations = json.load(file)

# Create an array of available languages
available_languages = list(translations.keys())
print("Available languages:", available_languages)

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
        .section-heading {font-size: 1.75rem; font-weight: bold; margin-top: 10px; margin-bottom: 10px;}
        .streamlit-expanderHeader {font-size: 1.5rem; font-weight: bold;} /* Custom font size for expander titles */
    </style>
""", unsafe_allow_html=True)

# Add a dropdown for language selection next to the main heading
language_options = "".join([f'<option value="{lang}" {"selected" if lang == "English" else ""}>{lang}</option>' for lang in available_languages])

st.markdown(
    f"""
    <style>
        .language-dropdown {{
            position: absolute;
            top: 10px;
            right: 20px;
            z-index: 1000;
        }}
    </style>
    <div class="language-dropdown">
        <select id="language-selector" onchange="window.location.reload();" style="padding: 5px 10px; font-size: 16px;">
            {language_options}
        </select>
    </div>
    """,
    unsafe_allow_html=True
)

# Add a section above the page title
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px; margin-top: -40px;">
        <h1 style="font-size: 2.5rem; color: #007BFF;">🩺 Diabetes Prediction App</h1>
        <p style="font-size: 1.2rem; color: #555;">This app predicts the likelihood of diabetes based on your health details.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
# Input form
def calculate_bmi(data):
    height_in_meters = data["Height"] * 0.3048  # Convert height from feet to meters
    data["BMI"] = data["Weight"] / (height_in_meters ** 2)
    return data

def user_input():
    st.header(current_translations["user_input_header"])
    st.write(current_translations["user_input_description"])

    data = {}

    with st.expander("General Information", expanded=True):
        data["Sex"] = st.selectbox("Gender", ["Male", "Female"], key="sex")
        data["Age"] = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1, key="age")
        data["Weight"] = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, key="weight")

        # Replace height input with dropdown for height in feet with increments of 0.1
        height_options = [round(x * 0.1, 1) for x in range(30, 76)]  # Generate options from 3.0 to 7.5
        data["Height"] = st.selectbox("Height (feet)", options=height_options, index=25, key="height_in_feet")

    # Calculate BMI
    data = calculate_bmi(data)

    with st.expander("Health Conditions", expanded=False):
        fields = {
            "HighBP": "High Blood Pressure",
            "HighChol": "High Cholesterol",
            "Smoker": "Smoker",
            "Stroke": "History of Stroke",
            "HeartDiseaseorAttack": "Heart Disease or Heart Attack",
            "PhysActivity": "Physically Active",
            "Fruits": "Consumes Fruits Regularly",
            "Veggies": "Consumes Vegetables Regularly",
            "HvyAlcoholConsump": "Heavy Alcohol Consumption",
            "DiffWalk": "Difficulty Walking",
        }
        cols = st.columns(2)  # Split into 2 columns
        for i, (field, label) in enumerate(fields.items()):
            col = cols[i % 2]
            data[field] = col.radio(label, ["Yes", "No"], index=1, key=field)

    # Hardcode "AnyHealthcare" to 1
    data["CholCheck"] = 1
    data["AnyHealthcare"] = 1
    data["NoDocbcCost"] = 0

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

# Ensure current_translations is defined based on the selected language
selected_language = st.session_state.get("language_selector", "English")
current_translations = translations[selected_language]

# Get user input
input_df = user_input()

# Predict button
if input_df is not None:
    st.markdown("---")
    st.subheader("**Predict Result**")

    if st.button("🔍 Predict Diabetes"):
        with st.spinner("Analyzing your data..."):
            prediction = model.predict(input_df)[0]

            # Determine BMI category
            bmi_value = round(input_df["BMI"].iloc[0], 2)
            if bmi_value < 18.5:
                bmi_category = "Underweight"
                bmi_color = "#FFA500"  # Orange
            elif 18.5 <= bmi_value <= 24.9:
                bmi_category = "Normal"
                bmi_color = "#008000"  # Darker green for better contrast
            elif 25 <= bmi_value <= 29.9:
                bmi_category = "Overweight"
                bmi_color = "#FFD700"  # Yellow
            else:
                bmi_category = "Obese"
                bmi_color = "#FF0000"  # Red

            # Display BMI and category below the prediction result
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 20px;">
                    <p style="font-size: 18px; color: {bmi_color}; font-weight: bold;">Your BMI is {bmi_value}, which falls under the category: {bmi_category}.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if prediction == 1:  # Diabetic
                st.markdown(
                    """
                    <div style="text-align: center; padding: 20px; background-color: #3d1e1e; border-radius: 10px;">
                        <img src="https://img.icons8.com/ios-filled/100/fa314a/error.png" width="50" style="margin-bottom: 10px;">
                        <h2 style="color: #ff4d4d; text-shadow: 1px 1px 2px #000000;"><b>Diabetic</b></h2>
                        <p style="font-size: 18px; color: #f8d4d4; text-shadow: 1px 1px 2px #000000;">Based on the information provided, the model predicts that you are at risk of diabetes.</p>
                        <p style="font-size: 16px; color: #d5a8a8; text-shadow: 1px 1px 2px #000000;">Please consult a healthcare professional for further advice and diagnosis.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:  # Non-Diabetic
                st.markdown(
                    """
                    <div style="text-align: center; padding: 20px; background-color: #1e3d1e; border-radius: 10px;">
                        <img src="https://img.icons8.com/ios-filled/100/00ff00/checked.png" width="50" style="margin-bottom: 10px;">
                        <h2 style="color: #00ff00; text-shadow: 1px 1px 2px #000000;"><b>Non-Diabetic</b></h2>
                        <p style="font-size: 18px; color: #d4f8d4; text-shadow: 1px 1px 2px #000000;">Based on the information provided, the model predicts that you are not at risk of diabetes.</p>
                        <p style="font-size: 16px; color: #a8d5a8; text-shadow: 1px 1px 2px #000000;">Maintain a healthy lifestyle and consult a healthcare professional for regular checkups.</p>
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
