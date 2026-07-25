from transformers import pipeline

pipe = pipeline("sentiment-analysis")

print(pipe("Python is very easy to learn."))
