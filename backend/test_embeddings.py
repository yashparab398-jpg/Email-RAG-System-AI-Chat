from app.embeddings.embedding_service import generate_embedding

embedding = generate_embedding(
    "This is a test email about energy trading."
)

print("Embedding dimensions:", len(embedding))

print(embedding[:10])