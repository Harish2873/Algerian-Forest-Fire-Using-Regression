import streamlit as st
import pandas as pd
import numpy as np
import joblib

# -----------------------------
# Load pre-trained scaler
# -----------------------------
scaler = joblib.load("Models/standardscalar.pkl")

# -----------------------------
# Model selection options
# -----------------------------
model_options = {
    "Linear Regression": "Models/linear_regression.pkl",
    "Lasso Regression": "Models/lasso.pkl",
    "Ridge Regression": "Models/ridge.pkl",
    "Elastic Net Regression": "Models/elastic_net.pkl"
}

st.title("🔥 Algerian Forest Fire FWI Prediction")
st.markdown("Select a regression model and input data to predict **Fire Weather Index (FWI)**.")

# -----------------------------
# User selects model
# -----------------------------
selected_model_name = st.selectbox("Select Regression Model", list(model_options.keys()))
model_file = model_options[selected_model_name]
model = joblib.load(model_file)

# -----------------------------
# User input form
# -----------------------------
st.header("🌿 Input Features")

def user_input_features():
    Temperature = st.number_input("Temperature (°C)", value=30.0)
    RH = st.number_input("Relative Humidity (%)", value=45.0)
    Ws = st.number_input("Wind Speed (km/h)", value=15.0)
    Rain = st.number_input("Rainfall (mm)", value=0.0)
    FFMC = st.number_input("FFMC Index", value=85.0)
    DMC = st.number_input("DMC Index", value=6.0)
    ISI = st.number_input("ISI Index", value=3.0)
    Classes = st.selectbox("Fire Class", ['not fire', 'fire'])
    Region = st.selectbox("Region", ['Bejaia', 'Sidi Bel-abbes'])

    class_val = 0 if Classes == "not fire" else 1
    region_val = 0 if Region == "Bejaia" else 1

    # Apply same log transform
    input_dict = {
        'Temperature': Temperature,
        'RH': RH,
        'Ws': Ws,
        'Rain': np.log1p(Rain),
        'FFMC': FFMC,
        'DMC': np.log1p(DMC),
        'ISI': np.log1p(ISI),
        'Classes': class_val,
        'Region': region_val
    }

    return pd.DataFrame([input_dict])

input_df = user_input_features()

# -----------------------------
# Predict and display
# -----------------------------
if st.button("Predict FWI"):
    X_scaled = scaler.transform(input_df)
    prediction = model.predict(X_scaled)[0]
    st.success(f"🔥 Predicted FWI: {prediction:.2f}")

    # Save to log (optional)
    input_df['Predicted_FWI'] = prediction
    try:
        existing = pd.read_csv("prediction_log.csv")
        new_log = pd.concat([existing, input_df], ignore_index=True)
    except FileNotFoundError:
        new_log = input_df
    new_log.to_csv("prediction_log.csv", index=False)
    st.info("✅ Prediction logged.")

# -----------------------------
# Show past predictions
# -----------------------------
if st.checkbox("Show Past Predictions"):
    try:
        log_df = pd.read_csv("prediction_log.csv")
        st.dataframe(log_df)
    except FileNotFoundError:
        st.warning("No predictions made yet.")
