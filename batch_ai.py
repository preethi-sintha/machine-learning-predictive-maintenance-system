import json
import ollama


def healthy_recommendation():
    return {
        "Root Cause Analysis": "Machine operating within normal parameters.",
        "Recommended Maintenance Action": "Continue routine preventive maintenance and periodic monitoring."
    }


def analyze_failed_machines(df_failed):

    machine_data = df_failed.to_dict(orient="records")

    prompt = f"""
You are a Senior Predictive Maintenance Engineer.

Analyze ONLY the failed machines below.

For EACH machine provide:

1. Root Cause Analysis
2. Recommended Maintenance Action

Return ONLY a valid JSON array.

DO NOT write:
- Here is the analysis
- Explanation
- Markdown
- Code fences
- Notes
- Any text before or after the JSON

The response must start with [

The response must end with ]

Example:

[
  {{
    "Machine ID": "M001",
    "Root Cause Analysis": "...",
    "Recommended Maintenance Action": "..."
  }}
]

Failed Machines:

{json.dumps(machine_data, indent=2)}
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    start = content.find("[")

    end = content.rfind("]") + 1

    json_text = content[start:end]

    return json.loads(json_text)