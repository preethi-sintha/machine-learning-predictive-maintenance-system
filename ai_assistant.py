from ollama import chat


def generate_ai_response(
    prediction,
    healthy_probability,
    failure_probability,
    machine_data,
    machine_specification
):

    prediction_text = (
        "No Machine Failure"
        if prediction == 0
        else "Machine Failure Predicted"
    )

    prompt = f"""
You are an industrial predictive maintenance expert.

Machine Details:

- Machine Type: {machine_data["Machine Type"]}
- Air Temperature: {machine_data["Air Temperature"]} K
- Process Temperature: {machine_data["Process Temperature"]} K
- Rotational Speed: {machine_data["Rotational Speed"]} RPM
- Torque: {machine_data["Torque"]} Nm
- Tool Wear: {machine_data["Tool Wear"]} minutes

Machine Specification Document:

{machine_specification}

Prediction:
{prediction_text}

Healthy Probability:
{healthy_probability:.2f}%

Failure Probability:
{failure_probability:.2f}%

Using BOTH the machine specification document and the prediction result:

1. Explain why the machine received this prediction.
2. Mention whether machine age, maintenance schedule, manufacturer recommendations, or service life contribute to the condition (if available in the document).
3. Explain the condition in simple language.
4. Recommend immediate maintenance actions.
5. Recommend long-term preventive maintenance.

Keep the explanation concise and practical.
"""

    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content