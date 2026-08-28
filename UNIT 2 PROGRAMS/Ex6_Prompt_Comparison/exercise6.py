import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# 1. LOAD API KEY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file.")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# 2. TEST DATA - 15 CUSTOMER MESSAGES
# ============================================================

TEST_MESSAGES = [
    {
        "id": 1,
        "message": "My order was supposed to arrive yesterday but it is still not here.",
        "category": "DELIVERY_DELAY",
        "urgency": "MEDIUM",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 2,
        "message": "I was charged twice for the same order. Please refund one payment.",
        "category": "PAYMENT_REFUND",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 3,
        "message": "The headphones arrived broken and one side is not working.",
        "category": "PRODUCT_DEFECT",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 4,
        "message": "I cannot log into my account because I forgot my password.",
        "category": "ACCOUNT_ACCESS",
        "urgency": "MEDIUM",
        "sentiment": "NEUTRAL",
    },
    {
        "id": 5,
        "message": "Great service! My package arrived earlier than expected.",
        "category": "FEEDBACK_OTHER",
        "urgency": "LOW",
        "sentiment": "POSITIVE",
    },
    {
        "id": 6,
        "message": "Where???",
        "category": "DELIVERY_DELAY",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 7,
        "message": "Order is late again lol, amazing service 🙄",
        "category": "DELIVERY_DELAY",
        "urgency": "MEDIUM",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 8,
        "message": "Payment successful but refund still not showing after 9 days.",
        "category": "PAYMENT_REFUND",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 9,
        "message": "Product arrived damaged, but I also need to change my delivery address.",
        "category": "PRODUCT_DEFECT",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 10,
        "message": "Enakku login panna mudiyala, password work aagala.",
        "category": "ACCOUNT_ACCESS",
        "urgency": "MEDIUM",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 11,
        "message": "Bhai payment cut gaya but order cancel ho gaya, refund kab milega?",
        "category": "PAYMENT_REFUND",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 12,
        "message": "The product works perfectly. Just wanted to say thank you!",
        "category": "FEEDBACK_OTHER",
        "urgency": "LOW",
        "sentiment": "POSITIVE",
    },
    {
        "id": 13,
        "message": "My order hasn't shipped and I need it urgently for tomorrow.",
        "category": "DELIVERY_DELAY",
        "urgency": "HIGH",
        "sentiment": "NEGATIVE",
    },
    {
        "id": 14,
        "message": "I think the item is defective, but I'm not sure if the strange noise is normal.",
        "category": "PRODUCT_DEFECT",
        "urgency": "MEDIUM",
        "sentiment": "NEUTRAL",
    },
    {
        "id": 15,
        "message": "Please tell me where my order is. I don't want to wait another week.",
        "category": "DELIVERY_DELAY",
        "urgency": "MEDIUM",
        "sentiment": "NEGATIVE",
    },
]


# ============================================================
# 3. COMMON INSTRUCTIONS
# ============================================================

COMMON_INSTRUCTIONS = """
You are a support-ticket triage engine for an e-commerce company.

Classify the customer message into exactly one CATEGORY:

DELIVERY_DELAY
PAYMENT_REFUND
PRODUCT_DEFECT
ACCOUNT_ACCESS
FEEDBACK_OTHER

Also assign:

URGENCY:
HIGH
MEDIUM
LOW

SENTIMENT:
POSITIVE
NEUTRAL
NEGATIVE

CATEGORY definitions:
- DELIVERY_DELAY: Problems involving delayed, late, missing,
  or unshipped orders.
- PAYMENT_REFUND: Payment failures, duplicate charges,
  refunds, or payment-related issues.
- PRODUCT_DEFECT: Damaged, broken, faulty, or defective products.
- ACCOUNT_ACCESS: Login, password, account access,
  or account recovery problems.
- FEEDBACK_OTHER: Positive feedback, general feedback,
  or issues not fitting the above categories.

Return ONLY valid JSON.
Do not provide explanations.
Do not use markdown.
Do not repeat or echo any order ID or personal information.

Required JSON format:
{
  "category": "CATEGORY",
  "urgency": "URGENCY",
  "sentiment": "SENTIMENT"
}
"""


# ============================================================
# 4. PROMPT BUILDERS
# ============================================================

def zero_shot_prompt(message):
    return (
        COMMON_INSTRUCTIONS
        + "\nCustomer message:\n"
        + message
    )


def one_shot_prompt(message):
    example = """
Example:

Customer message:
"Refund shows credited but nothing in my bank account since 9 days."

Output:
{"category":"PAYMENT_REFUND","urgency":"HIGH","sentiment":"NEGATIVE"}
"""

    return (
        COMMON_INSTRUCTIONS
        + example
        + "\nNow classify this customer message:\n"
        + message
    )


def few_shot_prompt(message):
    examples = """
Examples:

Customer message:
"Ordered on the 3rd, still not shipped, I need it for a wedding."

Output:
{"category":"DELIVERY_DELAY","urgency":"HIGH","sentiment":"NEGATIVE"}

Customer message:
"Refund shows credited but nothing in my bank account since 9 days."

Output:
{"category":"PAYMENT_REFUND","urgency":"HIGH","sentiment":"NEGATIVE"}

Customer message:
"The laptop screen arrived cracked and unusable."

Output:
{"category":"PRODUCT_DEFECT","urgency":"HIGH","sentiment":"NEGATIVE"}

Customer message:
"I forgot my password and cannot access my account."

Output:
{"category":"ACCOUNT_ACCESS","urgency":"MEDIUM","sentiment":"NEUTRAL"}

Customer message:
"Excellent service, my order arrived early!"

Output:
{"category":"FEEDBACK_OTHER","urgency":"LOW","sentiment":"POSITIVE"}
"""

    return (
        COMMON_INSTRUCTIONS
        + examples
        + "\nNow classify this customer message:\n"
        + message
    )


# ============================================================
# 5. CALL GROQ
# ============================================================

def call_groq(prompt):
    start_time = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
            top_p=1.0,
            max_tokens=150,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        text = response.choices[0].message.content.strip()

        usage = response.usage

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens

        return {
            "text": text,
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "error": "",
        }

    except Exception as error:
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "text": "",
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "error": str(error),
        }


# ============================================================
# 6. CHECK JSON AND ACCURACY
# ============================================================

def evaluate_output(text, expected):
    valid_json = False
    category_correct = False
    urgency_correct = False

    try:
        data = json.loads(text)

        required = {
            "category",
            "urgency",
            "sentiment",
        }

        if required.issubset(data.keys()):
            valid_json = True

            category_correct = (
                data["category"] == expected["category"]
            )

            urgency_correct = (
                data["urgency"] == expected["urgency"]
            )

    except (json.JSONDecodeError, TypeError):
        pass

    return valid_json, category_correct, urgency_correct


# ============================================================
# 7. RUN ONE STRATEGY
# ============================================================

def run_strategy(strategy_name, prompt_function):
    results = []

    print("\n" + "=" * 70)
    print(f"RUNNING {strategy_name.upper()}")
    print("=" * 70)

    for item in TEST_MESSAGES:

        print(f"\nTest {item['id']}/15")

        prompt = prompt_function(item["message"])

        result = call_groq(prompt)

        valid_json, category_correct, urgency_correct = (
            evaluate_output(result["text"], item)
        )

        row = {
            "strategy": strategy_name,
            "id": item["id"],
            "message": item["message"],
            "gold_category": item["category"],
            "gold_urgency": item["urgency"],
            "gold_sentiment": item["sentiment"],
            "output": result["text"],
            "valid_json": valid_json,
            "category_correct": category_correct,
            "urgency_correct": urgency_correct,
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "latency_ms": result["latency_ms"],
            "error": result["error"],
        }

        results.append(row)

        print("Output:", result["text"])
        print("Valid JSON:", valid_json)
        print("Category correct:", category_correct)
        print("Urgency correct:", urgency_correct)
        print("Latency:", result["latency_ms"], "ms")

        time.sleep(0.5)

    return results


# ============================================================
# 8. CALCULATE SUMMARY
# ============================================================

def calculate_summary(results):
    total = len(results)

    category_correct = sum(
        row["category_correct"] for row in results
    )

    urgency_correct = sum(
        row["urgency_correct"] for row in results
    )

    valid_json = sum(
        row["valid_json"] for row in results
    )

    mean_prompt_tokens = (
        sum(row["prompt_tokens"] for row in results) / total
    )

    mean_completion_tokens = (
        sum(row["completion_tokens"] for row in results) / total
    )

    mean_latency = (
        sum(row["latency_ms"] for row in results) / total
    )

    return {
        "category_accuracy": category_correct,
        "urgency_accuracy": urgency_correct,
        "valid_json_rate": (valid_json / total) * 100,
        "mean_prompt_tokens": mean_prompt_tokens,
        "mean_completion_tokens": mean_completion_tokens,
        "mean_latency_ms": mean_latency,
    }


# ============================================================
# 9. SAVE RESULTS
# ============================================================

def save_results(all_results):
    output_folder = Path(__file__).parent / "outputs"
    output_folder.mkdir(exist_ok=True)

    results_file = output_folder / "exercise6_results.json"

    with open(results_file, "w", encoding="utf-8") as file:
        json.dump(
            all_results,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\nResults saved to:")
    print(results_file)


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

def main():
    all_results = []

    strategies = [
        ("Zero-shot", zero_shot_prompt),
        ("One-shot", one_shot_prompt),
        ("Few-shot", few_shot_prompt),
    ]

    for strategy_name, prompt_function in strategies:

        results = run_strategy(
            strategy_name,
            prompt_function,
        )

        all_results.extend(results)

        summary = calculate_summary(results)

        print("\n" + "-" * 50)
        print(strategy_name)
        print("-" * 50)

        print(
            "Category accuracy:",
            f"{summary['category_accuracy']}/15",
        )

        print(
            "Urgency accuracy:",
            f"{summary['urgency_accuracy']}/15",
        )

        print(
            "Valid JSON rate:",
            f"{summary['valid_json_rate']:.2f}%",
        )

        print(
            "Mean prompt tokens:",
            f"{summary['mean_prompt_tokens']:.2f}",
        )

        print(
            "Mean completion tokens:",
            f"{summary['mean_completion_tokens']:.2f}",
        )

        print(
            "Mean latency:",
            f"{summary['mean_latency_ms']:.2f} ms",
        )

    save_results(all_results)

    print("\n" + "=" * 70)
    print("EXERCISE 6 COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()