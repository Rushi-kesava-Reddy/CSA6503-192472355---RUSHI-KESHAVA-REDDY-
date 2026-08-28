import json
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


# ============================================================
# 2. PRODUCTION REVIEW MEETING TRANSCRIPT
# ============================================================

TRANSCRIPT = """
Production Review Meeting Transcript

Date: 10 September 2026

The production review meeting was conducted to evaluate the performance
of the manufacturing plant during the first week of September. The meeting
was attended by Ravi Kumar, Plant Manager, Anita Sharma, Production
Engineer, Suresh Rao, Quality Manager, Priya Menon, Maintenance Manager,
and Arjun Das, Supply Chain Manager.

Ravi opened the meeting by reviewing the production target for the week.
The plant had planned to produce 1,200 motor assemblies. Actual production
was 1,080 assemblies, which represented 90 percent of the planned target.
Ravi explained that the shortfall was mainly caused by an unexpected
maintenance shutdown on the M-450 assembly line.

Anita reported that the M-450 line was stopped for 14 hours because of a
failure in the hydraulic pressure system. The maintenance team replaced
the hydraulic pump and tested the line before restarting production.
According to Priya, the replacement pump cost 48,000 rupees and the repair
was completed on 8 September at 6:30 PM.

The team then discussed production quality. Suresh reported that the
quality department inspected 1,050 assemblies during the week. A total of
42 defects were recorded. The defect rate was therefore approximately
4 percent. The largest defect category was incorrect shaft alignment,
which accounted for 18 assemblies. Surface scratches accounted for 11
assemblies, incorrect wiring accounted for 8 assemblies, and other minor
defects accounted for 5 assemblies.

Suresh explained that the shaft alignment problem was concentrated on the
M-450 line. The quality team recommended checking the alignment fixture
at the beginning of every production shift. Anita agreed to introduce
a fixture inspection checklist from 12 September.

The meeting also reviewed machine efficiency. The M-450 line operated at
an average efficiency of 82 percent during the week. The M-320 line
performed better, achieving 91 percent efficiency. Priya said that the
difference was partly due to the age of the M-450 equipment. The M-450
machine has been in operation for seven years, while the M-320 machine
has been operating for three years.

Priya proposed a preventive maintenance inspection of the M-450 line.
The inspection will include the hydraulic system, electrical connections,
bearings and alignment fixture. The inspection is scheduled for
15 September and is expected to take six hours.

Arjun then presented the raw material status. The plant currently has
enough steel sheets for approximately nine production days. However,
there is a shortage of a specific bearing used in the M-450 assembly.
The supplier has confirmed delivery of 600 bearings on 13 September.
The normal weekly requirement is approximately 450 bearings, so the
delivery should provide sufficient stock for the following week.

The team discussed shipment commitments. Three customer orders are
scheduled for dispatch between 12 September and 14 September. Ravi asked
Arjun to confirm that the material shortage would not affect those
shipments. Arjun confirmed that the existing stock is sufficient for
all three orders.

The safety report was also reviewed. There were no lost-time accidents
during the week. Two minor safety observations were recorded. One
observation involved an oil spill near the M-450 maintenance area.
The spill was cleaned immediately. The second observation involved
an operator who was not wearing safety glasses during a short inspection.
The supervisor provided a reminder about mandatory protective equipment.

Ravi concluded that the production target for the next week should remain
at 1,200 assemblies. Anita proposed improving output by reducing setup
time between batches. She estimated that setup optimization could save
approximately 30 minutes per batch. The engineering team will test the
new setup procedure on 16 September.

The quality team will monitor the shaft alignment defect rate daily.
Suresh set a target of reducing shaft alignment defects from 18 assemblies
per week to fewer than 10 assemblies per week by the end of September.

The meeting ended with five agreed actions. Anita will implement the
fixture inspection checklist by 12 September. Priya will complete the
M-450 preventive maintenance inspection on 15 September. Arjun will
confirm receipt of the 600 bearings on 13 September. Suresh will monitor
shaft alignment defects daily. The engineering team will test the setup
optimization procedure on 16 September.

Ravi requested that all action owners send a short status update before
the next production review meeting. The next meeting is scheduled for
20 September 2026.
"""


# ============================================================
# 3. GROQ CALL FUNCTION
# ============================================================

def ask_groq(prompt, temperature=0.2):
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=800,
        )

        latency = (time.perf_counter() - start) * 1000

        text = response.choices[0].message.content.strip()

        return {
            "output": text,
            "latency_ms": round(latency, 2),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "error": ""
        }

    except Exception as error:
        return {
            "output": "",
            "latency_ms": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "error": str(error)
        }


# ============================================================
# 4. EXERCISE 7A - SUMMARIZATION
# ============================================================

def run_summarization():

    print("\n" + "=" * 70)
    print("EXERCISE 7A - TEXT SUMMARIZATION")
    print("=" * 70)

    prompts = {

        "executive_abstract": f"""
You are a senior management communication assistant.

TASK:
Create an executive abstract of the production review meeting.

SOURCE:
{TRANSCRIPT}

CONSTRAINTS:
- Maximum 80 words.
- No technical jargon.
- Written for the Managing Director.
- Include the most important production, quality and action information.
- Do not invent facts.
- Use only information present in the source.

Return only the executive abstract.
""",

        "action_item_list": f"""
You are a professional meeting-minutes assistant.

TASK:
Extract all agreed action items from the meeting.

SOURCE:
{TRANSCRIPT}

CONSTRAINTS:
- Use bullet points.
- Every item must contain Owner, Task and Deadline.
- Do not invent owners or deadlines.
- Use only information present in the source.

Return only the action-item list.
""",

        "technical_summary": f"""
You are a technical production documentation assistant.

TASK:
Create a technical summary of the production review meeting.

SOURCE:
{TRANSCRIPT}

CONSTRAINTS:
- Retain machine names.
- Retain defect counts.
- Retain production numbers.
- Retain percentages.
- Retain dates and times.
- Retain costs.
- Retain numerical values.
- Do not invent information.
- Use only information present in the source.

Return only the technical summary.
"""
    }

    results = {}

    for name, prompt in prompts.items():

        print(f"\nGenerating: {name}")

        result = ask_groq(prompt)

        results[name] = result

        print("\nOUTPUT:")
        print(result["output"])

        if result["error"]:
            print("ERROR:", result["error"])

    return results


# ============================================================
# 5. EXERCISE 7B - PROFESSIONAL EMAIL
# ============================================================

EMAIL_CONTEXT = """
ROLE:
You are a senior account manager at a precision-components manufacturer.

CONTEXT:
Client = Meridian Auto
Relationship = 7-year account
Purchase Order = PO-4471
Quantity = 400 units
Original delivery date = 12 Sep
Revised delivery date = 21 Sep
Cause = sub-supplier casting failure

TASK:
Write the delay notification email.

CONSTRAINTS:
- Maximum 150 words.
- State the revised delivery date explicitly.
- Offer exactly one concrete remedy.
- The remedy should be expedited freight.
- Do not admit legal liability.
- Do not reference penalty clauses.
- Do not apologise more than twice.
- No placeholders such as [Name].
- Include a subject line.
"""


def run_email_generation():

    print("\n" + "=" * 70)
    print("EXERCISE 7B - PROFESSIONAL EMAIL")
    print("=" * 70)

    prompts = {

        "formal": EMAIL_CONTEXT + """
TONE:
Professional and formal.
Accountable but not grovelling.

OUTPUT:
Subject line followed by email body.
""",

        "empathetic": EMAIL_CONTEXT + """
TONE:
Professional and empathetic.
Acknowledge the inconvenience to the long-standing client.

OUTPUT:
Subject line followed by email body.
""",

        "assertive": EMAIL_CONTEXT + """
TONE:
Professional and confident.
Clearly communicate the situation and recovery action.

OUTPUT:
Subject line followed by email body.
"""
    }

    results = {}

    for tone, prompt in prompts.items():

        print(f"\nGenerating {tone} email...")

        result = ask_groq(prompt)

        results[tone] = result

        print("\nOUTPUT:")
        print(result["output"])

        if result["error"]:
            print("ERROR:", result["error"])

    return results


# ============================================================
# 6. EXERCISE 7C - CONTENT CREATION
# ============================================================

PRODUCT_DATASHEET = """
Product: EcoDrive Industrial Motor

Product type: Energy-efficient industrial motor
Efficiency: 94 percent
Power rating: 15 kW
Operating voltage: 415 V
Application: Industrial pumps and conveyor systems
Noise level: 68 dB
Warranty: 3 years
Energy saving: Up to 18 percent compared with older standard motors
Maintenance interval: 12 months
"""


def run_content_creation():

    print("\n" + "=" * 70)
    print("EXERCISE 7C - PRODUCT LAUNCH CAMPAIGN")
    print("=" * 70)

    prompt = f"""
You are a B2B industrial marketing specialist.

PRODUCT DATASHEET:
{PRODUCT_DATASHEET}

Create a coordinated product launch campaign.

Generate exactly three outputs:

1. LINKEDIN POST
- B2B tone.
- Specification-led.
- 120 to 150 words.

2. INSTAGRAM CAPTION
- Consumer-friendly tone.
- Maximum 40 words.
- Include hashtags.

3. WEBSITE BLURB
- Exactly 60 words.
- Include these three SEO keywords:
  energy efficient industrial motor
  industrial motor
  EcoDrive motor

IMPORTANT:
- All three outputs must remain factually consistent.
- Do not invent specifications.
- Do not contradict the product datasheet.
- Clearly label each output.
"""

    result = ask_groq(prompt)

    print("\nOUTPUT:")
    print(result["output"])

    if result["error"]:
        print("ERROR:", result["error"])

    return result


# ============================================================
# 7. ABLATION STUDY
# ============================================================

def run_ablation():

    print("\n" + "=" * 70)
    print("ABLATION STUDY")
    print("=" * 70)

    base_prompt = """
You are a senior account manager at a precision-components manufacturer.

Client = Meridian Auto.
The account has been active for 7 years.
Purchase order = PO-4471.
Quantity = 400 units.
Original delivery date = 12 Sep.
New delivery date = 21 Sep.
Cause = sub-supplier casting failure.

Write a professional delay notification email.

The email must:
- Be maximum 150 words.
- State the revised delivery date.
- Offer exactly one concrete remedy: expedited freight.
- Not admit legal liability.
- Not reference penalty clauses.
- Not apologise more than twice.
- Include a subject line and body.
- Use an accountable but professional tone.
"""

    components = [
        "Role",
        "Context",
        "Tone specification",
        "Word-count constraint",
        "Output-format specification"
    ]

    prompts = {

        "remove_role": """
Write a delay notification email.

Client = Meridian Auto.
Purchase order = PO-4471.
Quantity = 400 units.
Original delivery date = 12 Sep.
New delivery date = 21 Sep.
Cause = sub-supplier casting failure.

Be professional and accountable.
Maximum 150 words.
Offer exactly one remedy: expedited freight.
Do not admit legal liability.
Do not mention penalty clauses.
Include subject line and body.
""",

        "remove_context": """
You are a senior account manager at a precision-components manufacturer.

Write a professional delay notification email to a long-standing client.

The shipment is delayed by nine days because of a supplier failure.

Maximum 150 words.
State the revised delivery date.
Offer exactly one concrete remedy: expedited freight.
Do not admit legal liability.
Do not mention penalty clauses.
Do not apologise more than twice.
Include subject line and body.
""",

        "remove_tone": """
You are a senior account manager at a precision-components manufacturer.

Client = Meridian Auto.
Purchase order = PO-4471.
Quantity = 400 units.
Original delivery date = 12 Sep.
New delivery date = 21 Sep.
Cause = sub-supplier casting failure.

Write a delay notification email.
Maximum 150 words.
State the revised delivery date.
Offer exactly one concrete remedy: expedited freight.
Do not admit legal liability.
Do not mention penalty clauses.
Include subject line and body.
""",

        "remove_word_count": """
You are a senior account manager at a precision-components manufacturer.

Client = Meridian Auto.
Purchase order = PO-4471.
Quantity = 400 units.
Original delivery date = 12 Sep.
New delivery date = 21 Sep.
Cause = sub-supplier casting failure.

Write a professional and accountable delay notification email.

State the revised delivery date.
Offer exactly one concrete remedy: expedited freight.
Do not admit legal liability.
Do not mention penalty clauses.
Do not apologise more than twice.
Include subject line and body.
""",

        "remove_output_format": """
You are a senior account manager at a precision-components manufacturer.

Client = Meridian Auto.
Purchase order = PO-4471.
Quantity = 400 units.
Original delivery date = 12 Sep.
New delivery date = 21 Sep.
Cause = sub-supplier casting failure.

Write a professional and accountable delay notification email.

Maximum 150 words.
State the revised delivery date.
Offer exactly one concrete remedy: expedited freight.
Do not admit legal liability.
Do not mention penalty clauses.
Do not apologise more than twice.
"""
    }

    results = {}

    for name, prompt in prompts.items():

        print(f"\nTesting: {name}")

        result = ask_groq(prompt)

        results[name] = result

        print("\nOUTPUT:")
        print(result["output"])

        if result["error"]:
            print("ERROR:", result["error"])

    return results


# ============================================================
# 8. SAVE ALL RESULTS
# ============================================================

def save_results(summary, emails, campaign, ablation):

    output = {
        "exercise": "Exercise 7",
        "summarization": summary,
        "professional_emails": emails,
        "content_creation": campaign,
        "ablation_study": ablation
    }

    output_file = OUTPUT_DIR / "exercise7_results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("RESULTS SAVED")
    print("=" * 70)
    print(output_file)


# ============================================================
# 9. MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("EXERCISE 7 - BUSINESS PROMPT ENGINEERING")
    print("=" * 70)

    summarization_results = run_summarization()

    email_results = run_email_generation()

    campaign_results = run_content_creation()

    ablation_results = run_ablation()

    save_results(
        summarization_results,
        email_results,
        campaign_results,
        ablation_results
    )

    print("\n")
    print("=" * 70)
    print("EXERCISE 7 COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()