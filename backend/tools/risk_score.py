import pandas as pd
from backend.agents.base_agent import BaseAgent
import json
import os
from langchain_core.tools import tool

def load_csv(file_path: str) -> pd.DataFrame:
    """Load CSV into a DataFrame."""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns.")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load CSV file: {e}")

def prepare_llm_data(df: pd.DataFrame, suspicious_col: str = "suspicion_determined_datetime", normal_sample_size: int = 75) -> pd.DataFrame:
    """
    Prepare data for LLM: all suspicious rows + a sample of normal rows.
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
    """Convert the DataFrame to CSV string for LLM input."""
    return df.to_csv(index=False)

def save_json(data: dict, file_path: str):
    """Save Python dictionary as JSON file."""
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"💾 JSON saved to {file_path}")

def generate_behavior_rules(df_suspicious, df_normal, json_file_path="tools/suspicious_headers_rules_v2.json"):
    """
    Ask LLM to generate importance weights and behaviour rules for all headers.
    Saves output JSON to file.
    """
    sus_string = csv_to_string(df_suspicious)
    non_sus_string = csv_to_string(df_normal)
    
    agent = BaseAgent(tools=[], verbose=True)
    
    prompt = f"""
    You are a financial transaction analyst. Labeled transactions below:
    Suspicious transactions: {sus_string}
    Normal transactions: {non_sus_string}

    Tasks:
    1. Detect unusual patterns and suspicious activities.
    2. Assign an importance weight (0-1) to **all headers/features**, indicating how predictive they are for suspicious activity.
    3. Identify behaviour rules for each header that could trigger suspicion.
    4. Create **new headers by combining multiple existing headers** if a combination improves detection of suspicious activity. Assign them an importance weight and generate behaviour rules based on the combination.

    Return a JSON object in the following format:

    {{
    "HEADER_NAME_1": {{
        "importance_weight": 0.95,
        "behaviour_rules": [
        "rule 1",
        "rule 2"
        ]
    }},
    "HEADER_NAME_2": {{
        "importance_weight": 0.5,
        "behaviour_rules": ["rule 1"]
    }},
    "NEW_HEADER_COMBINATION": {{
        "importance_weight": 0.76,
        "behaviour_rules": [
        "rule combining HEADER_1 and HEADER_2 conditions triggered"
        ]
    }},
    ...
    }}

    Requirements:
    - Include **all original headers**.
    - Include **any new headers** created from combinations.
    - Only use **standard ASCII characters** (no special Unicode like \u202f or \u2011).
    - Only return **JSON**. No explanations or extra text.
    """

    response = agent.run(prompt)
    
    try:
        header_rules = json.loads(response)

        save_json(header_rules, json_file_path)
        return header_rules
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response as JSON. Returning raw output.")
        return {"raw_response": response}
    
def calculate_risk_score(transaction: dict, verbose=True) -> dict:
    json_file_path = "backend/tools/detect_suspicious.json"
    """
    Ask the LLM to check if a transaction triggers behaviour rules and calculate risk_score.
    Returns JSON with triggered rules and risk_score.
    """
    with open(json_file_path, "r") as f:
        rules_json = json.load(f)

    agent = BaseAgent(tools=[], verbose=verbose)
    
    prompt = f"""
        You are a financial transaction analyst AI.

        Given a single transaction and the following JSON of headers, importance weights, and behaviour rules:

        {json.dumps(rules_json, indent=2)}

        Transaction to analyze:
        {json.dumps(transaction, indent=2)}

        Tasks:
        1. Check which behaviour rules are triggered by the transaction.
        2. Calculate a risk score from 0 to 100:
        - Use importance_weight of each header.
        - Score should increase if rules are triggered.
        - Normalize to 0-100.
        3. Return a JSON object in the format:

        {{
        "triggered_rules": {{
            "HEADER_NAME": ["rule1 triggered", "rule2 triggered"],
            ...
        }},
        "risk_score": 85.5
        }}

        Only return JSON, no explanations.
        """
    response = agent.run(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response as JSON. Returning raw output.")
        return {"raw_response": response}

def main():
    # with open("backend/tools/example_transaction.json", "r") as f:
    #     example_transaction = json.load(f)
    csv_file = load_csv("transactions_mock_1000_for_participants.csv")
    suspicious, normal = prepare_llm_data(csv_file)

    generate_behavior_rules(suspicious, normal)
    # risk_result = calculate_risk_score(example_transaction)
    # save_json(risk_result, "risk_score_output.json")
    # print("\nRisk evaluation result for example transaction:")
    # print(risk_result)

if __name__ == "__main__":
    main()