from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

app = Flask(__name__)

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# AI question API
@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("question", "").strip()

    # Check empty question
    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    try:
        # Send question to Groq AI
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": """You are an AI Student Support Assistant for a university.

Your job is to:
- Answer academic questions clearly and simply.
- Help students understand programming concepts.
- Explain AI, machine learning, and computer science topics.
- Help with assignments and exam preparation.
- Give useful study guidance.
- Be friendly and supportive.
- If a question requires specific university information that you do not know, tell the student to contact the university administration."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],

            temperature=0.7,
            max_completion_tokens=1024
        )

        answer = response.choices[0].message.content

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("Groq Error:", str(e))

        return jsonify({
            "answer": f"Error: {str(e)}"
        }), 500


# Run application
if __name__ == "__main__":
    app.run(debug=True)