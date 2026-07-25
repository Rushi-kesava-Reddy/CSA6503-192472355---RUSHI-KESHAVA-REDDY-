from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompts = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning"
]

for p in prompts:
    print("\nPrompt:", p)
    result = generator(p, max_length=20)
    print(result[0]["generated_text"])
