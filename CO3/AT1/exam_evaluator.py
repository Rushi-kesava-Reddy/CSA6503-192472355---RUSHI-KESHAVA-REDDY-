from groq import Groq

# Paste your Groq API key here
client = Groq(api_key="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")


# Model answer
model_answer = """
Artificial Intelligence is the simulation of human intelligence
in machines that can learn, reason and make decisions.
"""


# Five student answers
student_answers = [
    "AI means machines that can learn, think and make decisions like humans.",
    
    "Artificial Intelligence is the simulation of human intelligence in machines.",
    
    "AI is used only for playing games.",
    
    "AI is a type of computer hardware.",
    
    "Artificial intelligence enables computers to perform tasks that normally require human intelligence."
]


# Evaluate each answer
for i, answer in enumerate(student_answers, 1):

    prompt = f"""
You are an exam answer evaluator.

Model Answer:
{model_answer}

Student Answer:
{answer}

The question carries 2 marks.

Give:
- 2 marks = completely correct
- 1 mark = partially correct
- 0 marks = incorrect

Important:
Different wording is acceptable if the meaning is correct.

Return ONLY:

Score: 0/1/2
Justification: one short sentence
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content

    print("\n--------------------------------")
    print("Answer", i)
    print("Student Answer:", answer)
    print(result)