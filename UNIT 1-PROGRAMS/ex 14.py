from transformers import pipeline

qa = pipeline("question-answering")

context = "Python is a programming language."

question = "What is Python?"

result = qa(question=question, context=context)

print(result)
