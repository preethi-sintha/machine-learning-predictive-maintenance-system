import streamlit as st
from predictor import predict_machine, batch_predict
from ai_assistant import generate_ai_response
import pandas as pd
from batch_ai import analyze_failed_machines, healthy_recommendation
from pdf_reader import extract_pdf_text

st.set_page_config(
    page_title="Predictive Maintenance Intelligence System",
    layout="wide"
)

# ======================================================
# Sidebar - System Configuration
# ======================================================

st.sidebar.title("System Configuration")

st.sidebar.markdown("------")

st.sidebar.subheader("Model Information")

st.sidebar.markdown("""
**Algorithm**  
Decision Tree Classifier

**Dataset**  
AI4I 2020 Predictive Maintenance

**Training Samples**  
10,000

**Input Features**  
6

**Prediction Classes**  
2

**Accuracy**  
98.4%
""")

st.sidebar.markdown("------")

# Store prediction result across Streamlit reruns

if "result" not in st.session_state:
    st.session_state.result = None
    
st.title("Predictive Maintenance Intelligence System")

st.markdown(
    """
Predict equipment health and receive **AI-assisted maintenance insights**.
"""
)

st.divider()

# ==========================================
# Prediction Mode
# ==========================================

st.subheader("Select Prediction Mode")

prediction_mode = st.radio(
    "",
    ["Single Machine Prediction", "Batch Prediction"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

if prediction_mode == "Single Machine Prediction":

# ==========================================
# Machine Specification
# ==========================================

    st.subheader("📄 Machine Specification")

    machine_spec = st.file_uploader(
        "Upload Machine Specification (PDF)",
        type=["pdf"],
        help="Upload the specification sheet of the selected machine."
    )

    if machine_spec is not None:

        st.success("✅ Machine specification uploaded successfully!")

        specification_text = extract_pdf_text(machine_spec)

        specification_text = specification_text.replace("(cid:127)", "")
        
        st.session_state["machine_specification"] = specification_text
          
    st.divider() 

    header_col1, header_col2 = st.columns([5, 1])

    with header_col1:
        st.subheader("📋 Enter Machine Parameters")

    with header_col2:
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        air_temperature = st.number_input(
            "Air Temperature (K)",
            min_value=250.0,
            max_value=350.0,
            value=300.0
        )

        rotational_speed = st.number_input(
            "Rotational Speed (RPM)",
            min_value=0,
            max_value=5000,
            value=1500
        )

        tool_wear = st.number_input(
            "Tool Wear (minutes)",
            min_value=0,
            max_value=300,
            value=100
        )

    with col2:
        process_temperature = st.number_input(
            "Process Temperature (K)",
            min_value=250.0,
            max_value=400.0,
            value=310.0
        )

        torque = st.number_input(
            "Torque (Nm)",  
            min_value=0.0,
            max_value=100.0,
            value=40.0
        )

        machine_type = st.selectbox(
            "Machine Type",
            ["L", "M", "H"]
        )

# ==========================
# Predict Button
# ==========================

    if st.button("🔍 Predict Machine Health"):

        st.session_state.result = predict_machine(
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            machine_type
        )

# ==========================
# Prediction Result
# ==========================

        if st.session_state.result is not None:

            result = st.session_state.result

            st.divider()

            st.subheader("📊 Prediction Result")

            if result["prediction"] == 0:
                st.success("🟢 No Machine Failure")
                st.info(
                    "The machine is operating under normal conditions. "
                    "No immediate maintenance action is required."
                )
            else:
                st.error("🔴 Machine Failure Predicted")
                st.warning(
                    "Immediate inspection and preventive maintenance are recommended "
                    "to avoid unexpected downtime."
                )

            st.markdown("### 📊 Healthy & Failure Probability")

            st.write(
                f"🟢 **Probability of No Machine Failure:** {result['healthy_probability']:.2f}%"
            )

            st.write(
                f"🔴 **Probability of Machine Failure:** {result['failure_probability']:.2f}%"
            )

# ==========================
# AI Assistant
# ==========================

    st.divider()

    st.subheader("AI Assistant")

    if st.button("Explain Prediction"):

        if st.session_state.result is None:
            st.warning("⚠️ Please predict the machine health first.")
        else:

            result = st.session_state.result

            with st.spinner("Generating AI explanation..."):

                response = generate_ai_response(
                    result["prediction"],
                    result["healthy_probability"],
                    result["failure_probability"],
                {
                        "Machine Type": machine_type,
                        "Air Temperature": air_temperature,
                        "Process Temperature": process_temperature,
                        "Rotational Speed": rotational_speed,
                        "Torque": torque,
                        "Tool Wear": tool_wear
                },
                st.session_state.get(
                    "machine_specification",
                    "No machine specification uploaded."
                )
            )

            st.success("AI Analysis")

            st.write(response)



else:
    st.subheader("📊 Batch Prediction")

    st.info(
        "Upload a CSV or Excel file containing sensor data for multiple machines."
    )

    batch_file = st.file_uploader(
        "Upload Sensor Dataset",
        type=["csv", "xlsx"]
    )

    if batch_file is not None:

        if batch_file.name.endswith(".csv"):
            df_batch = pd.read_csv(batch_file)
        else:
            df_batch = pd.read_excel(batch_file)

        required_columns = [
            "Machine ID",
            "Machine Type",
            "Air Temperature (K)",
            "Process Temperature (K)",
            "Rotational Speed (RPM)",
            "Torque (Nm)",
            "Tool Wear (min)"
        ] 
       
        missing_columns = [
            col for col in required_columns
            if col not in df_batch.columns
        ]

        if len(missing_columns) > 0:

            st.error("❌ Invalid dataset!")

            st.write("Missing Columns:")

            st.write(missing_columns)

        else:

            st.success("✅ Dataset validated successfully!")

            df_batch = df_batch.rename(columns={
                "Machine Type": "Type",
                "Air Temperature (K)": "Air temperature [K]",
                "Process Temperature (K)": "Process temperature [K]",
                "Rotational Speed (RPM)": "Rotational speed [rpm]",
                "Torque (Nm)": "Torque [Nm]",
                "Tool Wear (min)": "Tool wear [min]"
            })
            
            st.subheader("📊 Dataset Summary")

            total_machines = len(df_batch)
            total_features = len(df_batch.columns)
            missing_values = df_batch.isnull().sum().sum()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Machines", total_machines)

            with col2:
                st.metric("Total Features", total_features)

            with col3:
                st.metric("Missing Values", missing_values)

            if missing_values == 0:
                st.success("✅ Dataset is ready for prediction.")
            else:
                st.warning("⚠️ Dataset contains missing values.")

            st.divider()

            st.subheader("📄 Dataset Preview")

            st.dataframe(df_batch.head())

            st.divider()
 
            if st.button("⚙️ Predict All Machines", use_container_width=True):

                with st.spinner("Running batch prediction..."):

                    prediction_results = batch_predict(df_batch)
                    
                    prediction_results["Machine Status"] = prediction_results["Prediction"].map({
                        0: "🟢 Healthy",
                        1: "🔴 Failure"
                    })

                    failed_df = prediction_results[
                        prediction_results["Prediction"] == 1
                    ]
                    
                    if len(failed_df) > 0:

                        with st.spinner("🤖 AI is analyzing failed machines..."):

                            ai_response = analyze_failed_machines(failed_df)
                        
                        prediction_results["Root Cause Analysis"] = ""
                        prediction_results["Recommended Maintenance Action"] = ""

                        healthy_info = healthy_recommendation()

                        prediction_results.loc[
                            prediction_results["Prediction"] == 0,
                            "Root Cause Analysis"
                        ] = healthy_info["Root Cause Analysis"]

                        prediction_results.loc[
                            prediction_results["Prediction"] == 0,
                            "Recommended Maintenance Action"
                        ] = healthy_info["Recommended Maintenance Action"]

                        for item in ai_response:

                            machine_id = item["Machine ID"]

                            prediction_results.loc[
                                prediction_results["Machine ID"] == machine_id,
                                "Root Cause Analysis"
                            ] = item["Root Cause Analysis"]

                            prediction_results.loc[
                                prediction_results["Machine ID"] == machine_id,
                                "Recommended Maintenance Action"
                            ] = item["Recommended Maintenance Action"]
                    
                    total_machines = len(prediction_results)

                    healthy_count = (
                        prediction_results["Machine Status"] == "🟢 Healthy"
                    ).sum()

                    failure_count = (
                        prediction_results["Machine Status"] == "🔴 Failure"
                    ).sum()

                    failure_rate = (
                        failure_count / total_machines
                    ) * 100
                    
                st.success("✅ Batch prediction completed successfully!")

                st.subheader("📊 Prediction Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Machines", total_machines)

                with col2:
                    st.metric("Healthy", healthy_count)

                with col3:
                    st.metric("Failures", failure_count)

                with col4:
                    st.metric("Failure Rate", f"{failure_rate:.2f}%")

                st.divider()

                st.subheader("📄 Prediction Results")

                st.dataframe(
                    prediction_results,
                    use_container_width=True
                )

                from io import BytesIO

                output = BytesIO()

                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    prediction_results.to_excel(
                        writer,
                        index=False,
                        sheet_name="Prediction Report"
                )

                output.seek(0)

                st.download_button(
                    label="⬇ Download Prediction Report",
                    data=output,
                    file_name="Prediction_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )