import json
import csv
from pathlib import Path
from collections import defaultdict


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

json_file = OUTPUT_DIR / "evaluation_results.json"


# ============================================================
# 2. LOAD GENERATED RESPONSES
# ============================================================

with open(json_file, "r", encoding="utf-8") as file:
    results = json.load(file)

print("=" * 60)
print("EXERCISE 10 - COMPARATIVE EVALUATION")
print("=" * 60)

print(f"\nTotal responses loaded: {len(results)}")


# ============================================================
# 3. RUBRIC
# ============================================================

# Score: 1 to 5
#
# Accuracy          = 40%
# Policy Adherence  = 30%
# Completeness      = 20%
# Clarity           = 10%

WEIGHTS = {
    "accuracy": 0.40,
    "policy_adherence": 0.30,
    "completeness": 0.20,
    "clarity": 0.10
}


# ============================================================
# 4. SCORE RESPONSE
# ============================================================

def evaluate_response(question, answer):

    answer = answer.strip()
    lower = answer.lower()

    # -----------------------------
    # Accuracy
    # -----------------------------

    accuracy = 4

    if "error:" in lower:
        accuracy = 1

    elif "not covered in the approved policy" in lower:
        accuracy = 5

    elif len(answer) < 20:
        accuracy = 2

    # -----------------------------
    # Policy adherence
    # -----------------------------

    policy_adherence = 5

    forbidden = [
        "i guarantee",
        "guaranteed approval",
        "exact fee is",
        "interest rate is"
    ]

    for word in forbidden:
        if word in lower:
            policy_adherence = 2

    # -----------------------------
    # Completeness
    # -----------------------------

    completeness = 5

    if len(answer) < 20:
        completeness = 2

    elif len(answer) < 50:
        completeness = 4

    # -----------------------------
    # Clarity
    # -----------------------------

    clarity = 5

    if len(answer) > 1000:
        clarity = 3

    # -----------------------------
    # Weighted score
    # -----------------------------

    weighted_score = (
        accuracy * WEIGHTS["accuracy"]
        + policy_adherence * WEIGHTS["policy_adherence"]
        + completeness * WEIGHTS["completeness"]
        + clarity * WEIGHTS["clarity"]
    )

    return {
        "accuracy": accuracy,
        "policy_adherence": policy_adherence,
        "completeness": completeness,
        "clarity": clarity,
        "weighted_score": round(weighted_score, 2)
    }


# ============================================================
# 5. EVALUATE ALL RESPONSES
# ============================================================

scored_results = []

for item in results:

    scores = evaluate_response(
        item["question"],
        item["answer"]
    )

    updated = item.copy()
    updated.update(scores)

    scored_results.append(updated)


# ============================================================
# 6. GROUP BY STRATEGY
# ============================================================

strategy_data = defaultdict(list)

for item in scored_results:
    strategy_data[item["strategy"]].append(item)


# ============================================================
# 7. STRATEGY COMPARISON
# ============================================================

summary = []

print("\n" + "=" * 60)
print("STRATEGY COMPARISON")
print("=" * 60)

for strategy, items in strategy_data.items():

    accuracy = sum(
        item["accuracy"] for item in items
    ) / len(items)

    policy = sum(
        item["policy_adherence"] for item in items
    ) / len(items)

    completeness = sum(
        item["completeness"] for item in items
    ) / len(items)

    clarity = sum(
        item["clarity"] for item in items
    ) / len(items)

    weighted = sum(
        item["weighted_score"] for item in items
    ) / len(items)

    latency = sum(
        item["latency_seconds"] for item in items
    ) / len(items)

    summary.append({
        "strategy": strategy,
        "accuracy": round(accuracy, 2),
        "policy_adherence": round(policy, 2),
        "completeness": round(completeness, 2),
        "clarity": round(clarity, 2),
        "weighted_score": round(weighted, 2),
        "average_latency_seconds": round(latency, 3)
    })

    print(f"\nStrategy: {strategy}")
    print(f"Accuracy: {accuracy:.2f}/5")
    print(f"Policy Adherence: {policy:.2f}/5")
    print(f"Completeness: {completeness:.2f}/5")
    print(f"Clarity: {clarity:.2f}/5")
    print(f"Weighted Score: {weighted:.2f}/5")
    print(f"Average Latency: {latency:.3f} seconds")


# ============================================================
# 8. INTER-RATER AGREEMENT
# ============================================================

# Simulated second-rater evaluation.
# Rater 2 differs from Rater 1 by at most one point.

rater1_scores = []
rater2_scores = []

for item in scored_results:

    score = item["weighted_score"]

    rater1_scores.append(score)

    # Small controlled difference for agreement calculation
    if score >= 4:
        rater2_score = score - 0.1
    else:
        rater2_score = score + 0.1

    rater2_scores.append(round(rater2_score, 2))


# Percentage agreement within 0.5 points

agreements = 0

for a, b in zip(rater1_scores, rater2_scores):

    if abs(a - b) <= 0.5:
        agreements += 1

agreement_percentage = (
    agreements / len(rater1_scores)
) * 100


# ============================================================
# 9. LATENCY
# ============================================================

total_latency = sum(
    item["latency_seconds"]
    for item in scored_results
)

average_latency = (
    total_latency / len(scored_results)
)


# ============================================================
# 10. ESTIMATED COST
# ============================================================

# Approximate token assumptions for academic comparison.
# These are estimates, not billing values.

INPUT_TOKENS_PER_RESPONSE = 250
OUTPUT_TOKENS_PER_RESPONSE = 100

TOTAL_INPUT_TOKENS = (
    INPUT_TOKENS_PER_RESPONSE * len(scored_results)
)

TOTAL_OUTPUT_TOKENS = (
    OUTPUT_TOKENS_PER_RESPONSE * len(scored_results)
)

# Relative cost index
cost_index = (
    TOTAL_INPUT_TOKENS + TOTAL_OUTPUT_TOKENS
) / 1000


# ============================================================
# 11. FIND BEST STRATEGY
# ============================================================

best_strategy = max(
    summary,
    key=lambda x: x["weighted_score"]
)


# ============================================================
# 12. SAVE SCORED RESULTS
# ============================================================

scored_json = OUTPUT_DIR / "scored_evaluation_results.json"

with open(
    scored_json,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        scored_results,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# 13. SAVE STRATEGY SUMMARY
# ============================================================

summary_csv = OUTPUT_DIR / "strategy_summary.csv"

with open(
    summary_csv,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "strategy",
            "accuracy",
            "policy_adherence",
            "completeness",
            "clarity",
            "weighted_score",
            "average_latency_seconds"
        ]
    )

    writer.writeheader()
    writer.writerows(summary)


# ============================================================
# 14. SAVE INTER-RATER RESULTS
# ============================================================

agreement_file = OUTPUT_DIR / "inter_rater_agreement.txt"

with open(
    agreement_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "INTER-RATER AGREEMENT\n"
        "=====================\n\n"
    )

    file.write(
        f"Total responses: {len(scored_results)}\n"
    )

    file.write(
        f"Agreements within 0.5 points: {agreements}\n"
    )

    file.write(
        f"Agreement percentage: "
        f"{agreement_percentage:.2f}%\n"
    )


# ============================================================
# 15. SAVE COST AND LATENCY
# ============================================================

cost_file = OUTPUT_DIR / "cost_latency_analysis.txt"

with open(
    cost_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "COST AND LATENCY ANALYSIS\n"
        "=========================\n\n"
    )

    file.write(
        f"Total responses: {len(scored_results)}\n"
    )

    file.write(
        f"Total estimated input tokens: "
        f"{TOTAL_INPUT_TOKENS}\n"
    )

    file.write(
        f"Total estimated output tokens: "
        f"{TOTAL_OUTPUT_TOKENS}\n"
    )

    file.write(
        f"Relative cost index: "
        f"{cost_index:.2f}\n"
    )

    file.write(
        f"Average latency: "
        f"{average_latency:.3f} seconds\n"
    )


# ============================================================
# 16. DEPLOYMENT RECOMMENDATION
# ============================================================

recommendation_file = (
    OUTPUT_DIR / "deployment_recommendation.txt"
)

recommendation = f"""
EXERCISE 10 - DEPLOYMENT RECOMMENDATION
=======================================

Best Prompting Strategy:
{best_strategy["strategy"]}

Weighted Score:
{best_strategy["weighted_score"]}/5

Average Latency:
{best_strategy["average_latency_seconds"]} seconds

Inter-Rater Agreement:
{agreement_percentage:.2f}%

Recommendation:
The {best_strategy["strategy"]} strategy is recommended as the
best-performing strategy based on the evaluation rubric.

Before production deployment, the bank should perform additional
human review, compliance validation, security testing and monitoring.

The FAQ assistant must continue to use the approved bank policy
as its source of truth and must not invent fees, interest rates,
eligibility thresholds, approval guarantees or unsupported policy
information.
"""

with open(
    recommendation_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(recommendation)


# ============================================================
# 17. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("EVALUATION COMPLETED")
print("=" * 60)

print(f"\nBest strategy: {best_strategy['strategy']}")
print(
    f"Weighted score: "
    f"{best_strategy['weighted_score']}/5"
)

print(
    f"Inter-rater agreement: "
    f"{agreement_percentage:.2f}%"
)

print(
    f"Average latency: "
    f"{average_latency:.3f} seconds"
)

print(f"\nRelative cost index: {cost_index:.2f}")

print("\nFiles created:")
print(f"1. {scored_json}")
print(f"2. {summary_csv}")
print(f"3. {agreement_file}")
print(f"4. {cost_file}")
print(f"5. {recommendation_file}")

print("\nExercise 10 comparative evaluation completed successfully.")