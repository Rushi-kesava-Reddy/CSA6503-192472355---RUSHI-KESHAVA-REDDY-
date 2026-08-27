import os
import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 2. Create ChromaDB
# -----------------------------
client = chromadb.Client()

collection = client.get_or_create_collection(
    name="academic_calendar"
)

# -----------------------------
# 3. Read documents
# -----------------------------
folder = "documents"

documents = []
metadatas = []
ids = []

for filename in os.listdir(folder):

    if filename.endswith(".txt"):

        filepath = os.path.join(folder, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read()

        # Identify semester
        if "semester1" in filename.lower():
            semester = "Semester 1"
        elif "semester2" in filename.lower():
            semester = "Semester 2"
        else:
            semester = "General"

        documents.append(text)
        metadatas.append({
            "semester": semester,
            "source": filename
        })
        ids.append(filename)

# -----------------------------
# 4. Create embeddings
# -----------------------------
embeddings = model.encode(documents).tolist()

# -----------------------------
# 5. Store in vector database
# -----------------------------
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print("Academic calendar documents loaded successfully.")

# -----------------------------
# 6. Ask questions
# -----------------------------
while True:

    question = input("\nAsk your question (type 'exit' to stop): ")

    if question.lower() == "exit":
        break

    # Convert question into embedding
    query_embedding = model.encode([question]).tolist()

    # Search relevant documents
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )

    print("\nAnswer:")
    
    found = False

    for i in range(len(results["documents"][0])):

        document = results["documents"][0][i]
        semester = results["metadatas"][0][i]["semester"]

        # Check whether this document is relevant
        question_lower = question.lower()

        if "semester 1" in question_lower and semester == "Semester 1":
            print("\nSemester 1:")
            print(document)
            found = True

        elif "semester 2" in question_lower and semester == "Semester 2":
            print("\nSemester 2:")
            print(document)
            found = True

        elif "semester 1" not in question_lower and "semester 2" not in question_lower:
            print(f"\n{semester}:")
            print(document)
            found = True

    if not found:
        print("No matching academic calendar information found.")