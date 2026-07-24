from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "The future of AI"

result = generator(prompt, max_length=30)

print(result[0]["generated_text"])
