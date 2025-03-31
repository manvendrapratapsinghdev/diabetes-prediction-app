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

# Add a dropdown for language selection next to the main heading
st.markdown(
    """
    <style>
        .language-dropdown {
            position: absolute;
            top: -15px;
            right: 20px;
            z-index: 1000;
        }
    </style>
    <div class="language-dropdown">
        <select id="language-selector" onchange="window.location.reload();" style="padding: 5px 10px; font-size: 16px;">
            <option value="English" selected>English</option>
            <option value="Hindi">Hindi</option>
        </select>
    </div>
    """,
    unsafe_allow_html=True
)

# Add a section above the page title
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 2.5rem; color: #007BFF;">Welcome to the Diabetes Prediction App</h1>
        <p style="font-size: 1.2rem; color: #555;">Your health companion for predicting diabetes risk</p>
    </div>
    """,
    unsafe_allow_html=True
)

# st.title("🩺 Diabetes Prediction App")
# st.write("This app predicts the likelihood of diabetes based on your health details. Please fill in the information below.")




st.markdown("---")
# Input form
def user_input():
    # Apply color to BMI Interpretation based on bmi_interpretation from green to red
    st.header("**User Input Features**")
    st.write("Please provide the following information:")

    # Organize inputs into collapsible sections
    data = {}

    with st.expander("General Information", expanded=True):
        data["Sex"] = st.selectbox("Gender", ["Male", "Female"], key="sex")
        data["Age"] = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1, key="age")
        data["Weight"] = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, key="weight")

        # Replace height input with dropdown for height in feet with increments of 0.1
        height_options = [round(x * 0.1, 1) for x in range(30, 76)]  # Generate options from 3.0 to 7.5
        height_in_feet = st.selectbox("Height (feet)", options=height_options, index=25, key="height_in_feet")

        # Convert height in feet to meters and calculate BMI
        height_in_meters = height_in_feet * 0.3048  # Convert to meters
        data["BMI"] = data["Weight"] / (height_in_meters ** 2)

        # Adjust BMI interpretation based on sex
        bmi_interpretation = ""
        bmi_color = ""
        if data["Sex"] == "Male":
            if data["BMI"] < 20.7:
                bmi_interpretation = "Underweight"
                bmi_color = "#FF0000"  # Red
            elif 20.7 <= data["BMI"] <= 26.4:
                bmi_interpretation = "Normal weight"
                bmi_color = "#00FF00"  # Green
            elif 26.5 <= data["BMI"] <= 27.8:
                bmi_interpretation = "Slightly overweight"
                bmi_color = "#FFA500"  # Orange
            else:
                bmi_interpretation = "Overweight"
                bmi_color = "#FF0000"  # Red
        else:  # Female
            if data["BMI"] < 19.1:
                bmi_interpretation = "Underweight"
                bmi_color = "#FF0000"  # Red
            elif 19.1 <= data["BMI"] <= 25.8:
                bmi_interpretation = "Normal weight"
                bmi_color = "#00FF00"  # Green
            elif 25.9 <= data["BMI"] <= 27.3:
                bmi_interpretation = "Slightly overweight"
                bmi_color = "#FFA500"  # Orange
            else:
                bmi_interpretation = "Overweight"
                bmi_color = "#FF0000"  # Red

        # Display uneditable BMI data and interpretation with color
        st.text_input("BMI (calculated)", value=round(data["BMI"], 2), disabled=True, key="bmi_display")
        st.markdown(f'<div style=" margin-top: -30px; margin-left: 5px; color: {bmi_color}; font-weight: bold;">{bmi_interpretation}</div>', unsafe_allow_html=True)

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
