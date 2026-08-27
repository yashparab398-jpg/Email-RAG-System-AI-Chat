import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def _get_model():

    global _model

    if _model is None:

        print(
            "[EMBEDDING] Loading model...",
            flush=True
        )

        _model = SentenceTransformer(
            MODEL_NAME,
            device="cuda"
        )

        print(
            "[EMBEDDING] Model loaded.",
            flush=True
        )

    return _model


def generate_embedding(text):

    if not text:
        text = ""

    model = _get_model()

    embedding = model.encode(
        str(text),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embedding.tolist()