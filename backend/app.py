# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask app with a name
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained model pipeline (preprocessing + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the same order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (GET request)
@superkart_api.get("/")
def home():
    """Health-check endpoint to confirm the API is running."""
    return "Welcome to the SuperKart Sales Prediction API"


# Define an endpoint to predict sales for a single product-store combination (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    Accepts product and store details as JSON and returns the predicted
    Product_Store_Sales_Total for that product in that store.
    """
    # Get JSON data from the request
    data = request.get_json()

    # Check that all required features are present in the request
    missing = [feature for feature in FEATURES if feature not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Extract the relevant features from the input data and convert them into a DataFrame
    sample = {feature: data[feature] for feature in FEATURES}
    input_data = pd.DataFrame([sample])

    # Make a prediction using the trained model
    prediction = model.predict(input_data).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({"Sales": round(prediction, 2)})


# Define an endpoint to predict sales for a batch of products (POST request)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    Accepts a CSV file with product and store details and returns the predicted
    Product_Store_Sales_Total for every row, keyed by row index.
    """
    # Check that a file was uploaded with the key 'file'
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send the CSV with the key 'file'."}), 400

    # Read the uploaded CSV file into a DataFrame
    input_data = pd.read_csv(request.files["file"])

    # Check that all required features are present in the file
    missing = [feature for feature in FEATURES if feature not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Make predictions for all rows using only the features expected by the model
    predictions = model.predict(input_data[FEATURES]).tolist()

    # Create an output dictionary mapping each row index to its predicted sales
    output_dict = {str(i): round(pred, 2) for i, pred in enumerate(predictions)}

    return jsonify(output_dict)


# Run the Flask app in debug mode when executed directly (for local testing)
if __name__ == "__main__":
    superkart_api.run(debug=True)
