import os
import json
import pandas as pd
from backend.agents.base_agent import BaseAgent


# ----------------------------
# Utility Functions
# ----------------------------
def load_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns.")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load CSV file: {e}")

def prepare_llm_data(
    df: pd.DataFrame,
    suspicious_col: str = "suspicion_determined_datetime",
    normal_sample_size: int = 75
):
    """
    Prepare data for LLM: all suspicious rows + a sample of normal rows.
    Returns: suspicious_df, normal_sample_df
    """
    suspicious_df = df[df[suspicious_col].notna()]
    normal_df = df[df[suspicious_col].isna()]

    if len(normal_df) > normal_sample_size:
        normal_sample_df = normal_df.sample(n=normal_sample_size, random_state=42)
    else:
        normal_sample_df = normal_df

    print(f"⚡ Prepared {len(suspicious_df) + len(normal_sample_df)} rows for LLM "
          f"(Suspicious: {len(suspicious_df)}, Normal sampled: {len(normal_sample_df)})")
    return suspicious_df, normal_sample_df


def csv_to_string(df: pd.DataFrame) -> str:
    """Convert a DataFrame to CSV string for LLM input."""
    return df.to_csv(index=False)


def save_json(data: dict, file_path: str):
    """Save a Python dictionary as a JSON file. Creates folder if it doesn't exist."""
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"💾 JSON saved to {file_path}")


def normalize_json_unicode(json_str: str) -> str:
    """
    Replace special Unicode characters with standard ASCII equivalents.
    """
    replacements = {
        "\u2011": "-",   # non-breaking hyphen → normal hyphen
        "\u202f": " ",   # narrow non-breaking space → regular space
        "\u00a0": " "    # non-breaking space → regular space
    }
    for old, new in replacements.items():
        json_str = json_str.replace(old, new)
    return json_str


# ----------------------------
# LLM Behavior Rule Generation
# ----------------------------
def generate_behavior_rules(
    df_suspicious,
    df_normal,
    json_file_path="backend/tools/detect_suspicious.json"
):
    """Generate importance weights and behaviour rules for all headers via LLM."""
    sus_string = csv_to_string(df_suspicious)
    non_sus_string = csv_to_string(df_normal)
    agent = BaseAgent(tools=[], verbose=True)

    prompt = f"""
You are a financial transaction analyst. Labeled transactions below:
Suspicious transactions: {sus_string}
Normal transactions: {non_sus_string}

Tasks:
1. Detect unusual patterns and suspicious activities.
2. Assign an importance weight (0-1) to **all headers/features**.
3. Identify behaviour rules/conditions for each header that could trigger suspicion.
4. Create **new headers by combining multiple existing headers** if it improves detection. Assign importance weight and behaviour rules/conditions.

Return a JSON object in the format:

{{
  "HEADER_NAME_1": {{
    "importance_weight": 0.95,
    "behaviour_rules": ["rule 1", "rule 2"]
  }},
  "HEADER_NAME_2": {{
    "importance_weight": 0.5,
    "behaviour_rules": ["rule 1"]
  }},
  "NEW_HEADER_COMBINATION": {{
    "importance_weight": 0.76,
    "behaviour_rules": ["rule combining HEADER_1 and HEADER_2 conditions triggered"]
  }},
  ...
}}

Requirements:
- Include **all original headers** and **any new headers** created.
- Only use **ASCII characters** (no special Unicode like \\u202f or \\u2011).
- Only return **JSON**. No explanations.
"""

    response = agent.run(prompt)
    response = normalize_json_unicode(response)

    try:
        header_rules = json.loads(response)
        save_json(header_rules, json_file_path)
        return header_rules
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response as JSON. Returning raw output.")
        return {"raw_response": response}


# ----------------------------
# LLM Risk Score Calculation
# ----------------------------
def calculate_risk_score(transaction: dict, rules_file="backend/tools/detect_suspicious.json", verbose=True) -> dict:
    """
    Ask LLM to check if a transaction triggers behaviour rules and calculate risk_score.
    Returns JSON with triggered rules and risk_score.
    """
    with open(rules_file, "r") as f:
        rules_json = json.load(f)

    agent = BaseAgent(tools=[], verbose=verbose)
    prompt = f"""
You are a financial transaction analyst AI.

Given a single transaction and the following JSON of headers, importance weights, and behaviour rules:

{json.dumps(rules_json, indent=2)}

Transaction to analyze:
{json.dumps(transaction, indent=2)}

Tasks:
1. Check which behaviour rules are triggered. 
   - Behaviour rules may involve conditions combining multiple headers.
   - Evaluate each rule based on the values of all relevant headers in the transaction.
2. Calculate a risk score from 0 to 100:
   - Use the **importance_weight** of each header.
   - For all headers that have at least one triggered rule, sum their importance_weights.
   - Divide by the number of triggered headers.
   - Multiply the result by 100 to get a 0-100 score.
3. Return a JSON object in the format:

{{
  "triggered_rules": {{
      "HEADER_NAME": ["rule1 triggered", "rule2 triggered"],
      ...
  }},
  "risk_score": 85.5
}}

Only return JSON.
"""

    response = agent.run(prompt)
    response = normalize_json_unicode(response)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response as JSON. Returning raw output.")
        return {"raw_response": response}
    
def create_suspicious():
    csv_file = load_csv("transactions_mock_1000_for_participants.csv")
    suspicious, normal = prepare_llm_data(csv_file)
    generate_behavior_rules(suspicious, normal)

def main():
    with open("backend/tools/example_transaction.json", "r") as f:
        example_transaction = json.load(f)

    risk_result = calculate_risk_score(example_transaction)
    save_json(risk_result, "backend/tools/risk_score_output.json")

    print("\nRisk evaluation result for example transaction:")
    print(risk_result)

if __name__ == "__main__":
    main()
