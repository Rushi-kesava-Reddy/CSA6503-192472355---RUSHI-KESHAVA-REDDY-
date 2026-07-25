from transformers import pipeline

classifier = pipeline("sentiment-analysis")

result = classifier("I love learning Artificial Intelligence.")

print(result)
