import os
import requests
import pandas as pd
import streamlit as st

# Base URL of the Flask backend
# "backend" is the name of the backend container; Docker's internal DNS resolves it on the shared network
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

# Page configuration and title
st.set_page_config(page_title="SuperKart Sales Forecast")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales of a product in a store using the trained machine learning model.")

# ---------------------------------------------------------------
# Online (single) prediction
# ---------------------------------------------------------------
st.subheader("Online Prediction")
st.write("Enter the product and store details below to predict the total sales.")

# Input fields for product details
st.markdown("**Product details**")
col1, col2 = st.columns(2)
with col1:
    Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    Product_Allocated_Area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                             value=0.027, step=0.001, format="%.3f")
    Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
with col2:
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Id_char = st.selectbox("Product Category Code", ["FD", "DR", "NC"],
                                   help="FD = Food, DR = Drinks, NC = Non-Consumables")
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Input fields for store details
st.markdown("**Store details**")
col3, col4 = st.columns(2)
with col3:
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
with col4:
    Store_Type = st.selectbox("Store Type", ["Departmental Store", "Food Mart",
                                             "Supermarket Type1", "Supermarket Type2"], index=3)
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16, step=1)

# Create the JSON payload with the input values
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

# Send the request to the backend when the button is clicked
if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted Product Store Sales Total: {predicted_sales:,.2f}")
        else:
            st.error(f"Prediction failed (status {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the prediction API: {e}")

# ---------------------------------------------------------------
# Batch prediction
# ---------------------------------------------------------------
st.subheader("Batch Prediction")
st.write("Upload a CSV file containing the product and store details for multiple records.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Preview the uploaded data
    batch_data = pd.read_csv(uploaded_file)
    st.write("Preview of the uploaded data:")
    st.dataframe(batch_data.head())

    if st.button("Predict for Batch", type="primary"):
        try:
            # Rewind the file and send it to the backend batch endpoint
            uploaded_file.seek(0)
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                     files={"file": uploaded_file}, timeout=60)
            if response.status_code == 200:
                predictions = response.json()

                # Add the predictions as a new column next to the input data
                results = batch_data.copy()
                results["Predicted_Sales"] = [predictions[str(i)] for i in range(len(results))]

                st.success(f"Predictions generated for {len(results)} records.")
                st.dataframe(results)

                # Allow the user to download the results as a CSV file
                st.download_button("Download Predictions as CSV",
                                   data=results.to_csv(index=False).encode("utf-8"),
                                   file_name="superkart_predictions.csv", mime="text/csv")
            else:
                st.error(f"Batch prediction failed (status {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the prediction API: {e}")
