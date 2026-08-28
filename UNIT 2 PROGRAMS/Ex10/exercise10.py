import os
import time
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# 1. LOAD API KEY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)


# ============================================================
# 2. LOAD APPROVED BANK POLICY
# ============================================================

policy_path = Path(__file__).resolve().parent / "policy.txt"

with open(policy_path, "r", encoding="utf-8") as file:
    policy = file.read()


# ============================================================
# 3. FIXED BANK FAQ TASK
# ============================================================

questions = [
    "What are the eligibility requirements for a personal loan?",
    "What documents are required for KYC?",
    "Does meeting the eligibility criteria guarantee loan approval?",
    "Can the bank request additional KYC documents?",
    "What factors are considered for loan eligibility?",
    "What happens if my KYC documents are invalid?",
    "What are the service charges for banking services?",
    "Can you tell me the exact service charge?",
    "Are service charges the same for all accounts?",
    "Can you guarantee that my loan will be approved?"
]


# ============================================================
# 4. FIVE PROMPTING STRATEGIES
# ============================================================

strategies = {

    "zero_shot": """
Answer the customer's question using the approved bank policy.
Do not invent information.
""",

    "few_shot": """
Answer the customer's question using the approved bank policy.

Example:
Question: Does meeting the eligibility criteria guarantee loan approval?
Answer: No. Meeting the eligibility criteria does not guarantee loan approval.
The final approval decision is made by the bank after verification.

Now answer the customer's question.
""",

    "role_prompting": """
You are a compliant bank FAQ assistant.
Answer the customer's question using only the approved bank policy.
Never invent fees, rates, thresholds, guarantees or processing times.
If the answer is not covered, say exactly:
"Not covered in the approved policy."
""",

    "chain_of_thought": """
Answer the customer's question using the approved bank policy.
First identify the relevant policy information internally.
Then provide only a concise final answer.
Do not reveal private reasoning.
Do not invent information.
""",

    "rag_style": """
Use the following approved policy as your only source of truth.

APPROVED POLICY:
{policy}

Answer the customer's question using only this policy.
If the answer is not covered, say exactly:
"Not covered in the approved policy."
"""
}


# ============================================================
# 5. OUTPUT DIRECTORY
# ============================================================

output_dir = Path(__file__).resolve().parent / "outputs"
output_dir.mkdir(exist_ok=True)


# ============================================================
# 6. GENERATE RESPONSES
# ============================================================

results = []

print("=" * 60)
print("EXERCISE 10 - COMPARATIVE EVALUATION")
print("=" * 60)

for strategy_name, prompt_template in strategies.items():

    print(f"\nRunning strategy: {strategy_name}")

    for question in questions:

        if "{policy}" in prompt_template:
            prompt = prompt_template.format(policy=policy)
        else:
            prompt = prompt_template

        start_time = time.time()

        try:
            response = client.responses.create(
                model="openai/gpt-oss-20b",
                instructions=prompt,
                input=question
            )

            answer = response.output_text

        except Exception as e:
            answer = f"ERROR: {str(e)}"

        latency = time.time() - start_time

        results.append({
            "strategy": strategy_name,
            "question": question,
            "answer": answer,
            "latency_seconds": round(latency, 3)
        })

        print(f"  Question completed: {question[:50]}...")
        print(f"  Latency: {latency:.2f} seconds")


# ============================================================
# 7. SAVE JSON OUTPUT
# ============================================================

json_path = output_dir / "evaluation_results.json"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4, ensure_ascii=False)


# ============================================================
# 8. SAVE CSV OUTPUT
# ============================================================

import csv

csv_path = output_dir / "evaluation_results.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "strategy",
            "question",
            "answer",
            "latency_seconds"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


# ============================================================
# 9. SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("EXERCISE 10 COMPLETED")
print("=" * 60)

print(f"\nTotal responses generated: {len(results)}")

print("\nFiles created:")

print(f"1. {json_path}")
print(f"2. {csv_path}")

print("\nAll five prompting strategies were evaluated.")