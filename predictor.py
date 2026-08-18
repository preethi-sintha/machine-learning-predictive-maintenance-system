import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/decision_tree_model.pkl")

# Load fitted scaler
scaler = joblib.load("models/scaler.pkl")
def predict_machine(
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
    machine_type
):
    # One-Hot Encode Machine Type
    type_l = 1 if machine_type.upper() == "L" else 0
    type_m = 1 if machine_type.upper() == "M" else 0

    new_machine = pd.DataFrame({
        "Air temperature": [air_temperature],
        "Process temperature": [process_temperature],
        "Rotational speed": [rotational_speed],
        "Torque": [torque],
        "Tool wear": [tool_wear],
        "Type_L": [type_l],
        "Type_M": [type_m]
    })

    # Scale Input Data
    new_machine_scaled = scaler.transform(new_machine)

    # Predict Machine Condition
    prediction = model.predict(new_machine_scaled)[0]

    # Predict Probabilities
    probabilities = model.predict_proba(new_machine_scaled)[0]

    healthy_probability = probabilities[0] * 100
    failure_probability = probabilities[1] * 100

    return {
        "prediction": prediction,
        "healthy_probability": round(healthy_probability, 2),
        "failure_probability": round(failure_probability, 2)
    }

def batch_predict(df):

    results = []

    for _, row in df.iterrows():

        prediction = predict_machine(
            row["Air temperature [K]"],
            row["Process temperature [K]"],
            row["Rotational speed [rpm]"],
            row["Torque [Nm]"],
            row["Tool wear [min]"],
            row["Type"]
        )

        results.append({
            "Prediction": prediction["prediction"],
            "Healthy Probability (%)": prediction["healthy_probability"],
            "Failure Probability (%)": prediction["failure_probability"]
        })

    results_df = pd.DataFrame(results)

    return pd.concat(
        [df.reset_index(drop=True), results_df],
        axis=1
    )