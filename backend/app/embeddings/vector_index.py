import faiss
import numpy as np
from pymongo import MongoClient

from app.chunks.chunker import create_chunks
from app.embeddings.embedding_service import generate_embedding


client = MongoClient("mongodb://localhost:27017")

db = client["enron_email_intelligence"]

emails = db["emails"]

chunks_collection = db["chunks"]


def build_vector_index():

    documents = list(
        emails.find().limit(20000)
    )

    all_vectors = []

    all_chunks = []

    for document in documents:

        chunks = create_chunks(document)

        for chunk in chunks:

            try:
                vector = generate_embedding(
                    chunk["chunk_text"]
                )

                chunk["embedding"] = vector

                all_chunks.append(chunk)

                all_vectors.append(vector)

            except Exception as error:

                print(
                    f"Skipping chunk because of an error: {error}"
                )

    if not all_vectors:

        raise ValueError(
            "No vectors were generated."
        )

    vectors = np.array(
        all_vectors,
        dtype="float32"
    )

    index = faiss.IndexFlatL2(
        vectors.shape[1]
    )

    index.add(vectors)

    faiss.write_index(
        index,
        "vector_index.faiss"
    )

    chunks_collection.delete_many({})

    chunks_collection.insert_many(
        all_chunks
    )

    print(
        f"Indexed {len(documents)} emails."
    )

    print(
        f"Created {len(all_chunks)} chunks."
    )

    return len(all_chunks)


if __name__ == "__main__":

    build_vector_index()