from app.embeddings.vector_index import (
    build_vector_index
)

total = build_vector_index()

print(
    f"Indexed chunks: {total}"
)