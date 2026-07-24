from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

print(generator("Today is", max_length=20)[0]["generated_text"])
