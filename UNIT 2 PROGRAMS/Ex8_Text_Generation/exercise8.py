import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# 1. LOAD GROQ API KEY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file.")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"

OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_FILE = OUTPUT_DIR / "advisories.csv"


# ============================================================
# 2. PROMPT TEMPLATE
# ============================================================

PROMPT = """
You are an agricultural extension officer.

Write ONE advisory SMS under 160 characters in {language}.

Crop: {crop}
District: {district}
Soil: {soil}
Weather: {weather}

Rules:
- Give one actionable instruction.
- No greetings.
- No emojis.
- Use plain words.
- Do not invent facts.
- Do not give chemical dosage without units.
- Keep the message below 160 characters.
"""


# ============================================================
# 3. FALLBACK TEMPLATE
# ============================================================

FALLBACK_TEMPLATE = (
    "{crop} farmers in {district}: monitor the crop regularly "
    "and follow local agricultural guidance for current weather conditions."
)


# ============================================================
# 4. FARMER PROFILES
# ============================================================

FARMER_PROFILES = [
    {
        "id": 1,
        "crop": "Rice",
        "district": "Nellore",
        "soil": "Clay",
        "weather": "Heavy rain expected",
        "language": "English",
    },
    {
        "id": 2,
        "crop": "Cotton",
        "district": "Warangal",
        "soil": "Black soil",
        "weather": "Dry and sunny",
        "language": "English",
    },
    {
        "id": 3,
        "crop": "Groundnut",
        "district": "Anantapur",
        "soil": "Red soil",
        "weather": "Hot and dry",
        "language": "English",
    },
    {
        "id": 4,
        "crop": "Chilli",
        "district": "Guntur",
        "soil": "Loamy",
        "weather": "Cloudy with moderate rain",
        "language": "English",
    },
    {
        "id": 5,
        "crop": "Maize",
        "district": "Karimnagar",
        "soil": "Black soil",
        "weather": "Moderate rainfall",
        "language": "English",
    },
    {
        "id": 6,
        "crop": "Tomato",
        "district": "Kolar",
        "soil": "Red loam",
        "weather": "Humid and cloudy",
        "language": "English",
    },
    {
        "id": 7,
        "crop": "Paddy",
        "district": "Thanjavur",
        "soil": "Alluvial",
        "weather": "Continuous rain",
        "language": "English",
    },
    {
        "id": 8,
        "crop": "Sugarcane",
        "district": "Kolhapur",
        "soil": "Loamy",
        "weather": "Warm with moderate rain",
        "language": "English",
    },
    {
        "id": 9,
        "crop": "Soybean",
        "district": "Indore",
        "soil": "Black soil",
        "weather": "Intermittent rain",
        "language": "English",
    },
    {
        "id": 10,
        "crop": "Wheat",
        "district": "Ludhiana",
        "soil": "Alluvial",
        "weather": "Cool and dry",
        "language": "English",
    },
]


# ============================================================
# 5. ESTIMATED COST
# ============================================================

# Approximate educational estimate.
# Actual Groq pricing may vary by model/account.
INPUT_COST_PER_MILLION = 0.0
OUTPUT_COST_PER_MILLION = 0.0


def calculate_cost(prompt_tokens, completion_tokens):
    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_COST_PER_MILLION

    output_cost = (
        completion_tokens / 1_000_000
    ) * OUTPUT_COST_PER_MILLION

    return round(input_cost + output_cost, 8)


# ============================================================
# 6. FALLBACK MESSAGE
# ============================================================

def fallback_message(params):
    return FALLBACK_TEMPLATE.format(**params)


# ============================================================
# 7. GENERATE ADVISORY
# ============================================================

def generate_advisory(
    params,
    temperature=0.3,
    top_p=1.0,
):
    prompt = PROMPT.format(**params)

    last_error = ""

    for attempt in range(3):

        try:
            start_time = time.perf_counter()

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=120,
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            text = response.choices[0].message.content.strip()

            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = (
                response.usage.completion_tokens
            )

            cost = calculate_cost(
                prompt_tokens,
                completion_tokens,
            )

            return {
                "text": text,
                "latency_ms": round(latency_ms, 2),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "estimated_cost": cost,
                "fallback": False,
                "error": "",
            }

        except Exception as error:

            last_error = str(error)

            print(
                f"API error on attempt {attempt + 1}: "
                f"{last_error}"
            )

            # Simple exponential backoff.
            # This also prevents rapid repeated calls.
            if attempt < 2:
                wait_time = 2 ** attempt
                time.sleep(wait_time)

    # API unavailable after 3 attempts
    return {
        "text": fallback_message(params),
        "latency_ms": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "estimated_cost": 0,
        "fallback": True,
        "error": last_error,
    }


# ============================================================
# 8. CHECK SMS LENGTH
# ============================================================

def check_length(text):
    return len(text)


# ============================================================
# 9. PARAMETER SWEEP
# ============================================================

def run_parameter_sweep():

    print("\n")
    print("=" * 70)
    print("EXERCISE 8 - PARAMETER SWEEP")
    print("=" * 70)

    test_profile = FARMER_PROFILES[0]

    settings = [
        (0.0, 1.0),
        (0.4, 1.0),
        (0.9, 1.0),
        (0.4, 0.5),
        (0.9, 0.5),
    ]

    results = []

    for temperature, top_p in settings:

        print("\n" + "-" * 70)
        print(
            f"Temperature = {temperature} | "
            f"Top-p = {top_p}"
        )

        result = generate_advisory(
            test_profile,
            temperature=temperature,
            top_p=top_p,
        )

        text = result["text"]

        row = {
            "temperature": temperature,
            "top_p": top_p,
            "output": text,
            "first_40_chars": text[:40],
            "chars": len(text),
            "latency_ms": result["latency_ms"],
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "estimated_cost": result["estimated_cost"],
            "fallback": result["fallback"],
        }

        results.append(row)

        print("Output:")
        print(text)
        print("Characters:", len(text))
        print(
            "Latency:",
            result["latency_ms"],
            "ms",
        )
        print(
            "Prompt tokens:",
            result["prompt_tokens"],
        )
        print(
            "Completion tokens:",
            result["completion_tokens"],
        )

    return results


# ============================================================
# 10. BATCH GENERATION FOR 10 FARMERS
# ============================================================

def run_batch_generation():

    print("\n")
    print("=" * 70)
    print("BATCH GENERATION - 10 FARMER PROFILES")
    print("=" * 70)

    rows = []

    for profile in FARMER_PROFILES:

        print(
            f"\nGenerating advisory "
            f"for Farmer {profile['id']}..."
        )

        result = generate_advisory(
            profile,
            temperature=0.4,
            top_p=1.0,
        )

        text = result["text"]

        row = {
            "farmer_id": profile["id"],
            "crop": profile["crop"],
            "district": profile["district"],
            "soil": profile["soil"],
            "weather": profile["weather"],
            "language": profile["language"],
            "advisory": text,
            "characters": len(text),
            "under_160_chars": len(text) < 160,
            "temperature": 0.4,
            "top_p": 1.0,
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result[
                "completion_tokens"
            ],
            "latency_ms": result["latency_ms"],
            "estimated_cost": result[
                "estimated_cost"
            ],
            "fallback_used": result["fallback"],
            "error": result["error"],
        }

        rows.append(row)

        print("Advisory:")
        print(text)
        print("Characters:", len(text))

        time.sleep(0.5)

    return rows


# ============================================================
# 11. SAVE CSV
# ============================================================

def save_csv(rows):

    fieldnames = [
        "farmer_id",
        "crop",
        "district",
        "soil",
        "weather",
        "language",
        "advisory",
        "characters",
        "under_160_chars",
        "temperature",
        "top_p",
        "prompt_tokens",
        "completion_tokens",
        "latency_ms",
        "estimated_cost",
        "fallback_used",
        "error",
    ]

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nCSV saved successfully:")
    print(CSV_FILE)


# ============================================================
# 12. SAVE PARAMETER SWEEP
# ============================================================

def save_sweep(results):

    sweep_file = OUTPUT_DIR / "parameter_sweep.csv"

    fieldnames = [
        "temperature",
        "top_p",
        "output",
        "first_40_chars",
        "chars",
        "latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "estimated_cost",
        "fallback",
    ]

    with open(
        sweep_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print("Parameter sweep saved:")
    print(sweep_file)


# ============================================================
# 13. MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("EXERCISE 8 - TEXT GENERATION USING GROQ LLM API")
    print("=" * 70)

    print("\nModel:", MODEL)

    # Parameter sweep
    sweep_results = run_parameter_sweep()

    save_sweep(sweep_results)

    # Generate 10 farmer advisories
    batch_results = run_batch_generation()

    save_csv(batch_results)

    print("\n")
    print("=" * 70)
    print("EXERCISE 8 COMPLETED")
    print("=" * 70)

    print("\nFiles created:")
    print("1. outputs\\parameter_sweep.csv")
    print("2. outputs\\advisories.csv")


if __name__ == "__main__":
    main()