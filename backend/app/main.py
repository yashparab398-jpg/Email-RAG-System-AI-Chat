import threading
import time
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.websocket import router as websocket_router
from app.api.query import router as query_router
from app.api.hubs import router as hubs_router
from app.api.entities import router as entities_router
from app.api.timeline import router as timeline_router
from app.health import router as health_router
from app.api.emails import router as emails_router
from app.api.insights import router as insights_router
from app.api.ingestion import router as ingestion_router
from app.api.risk import router as risk_router


app = FastAPI(
    title="Enron Email Intelligence System",
    version="1.0.0"
)


# =========================================================
# OLLAMA CONFIGURATION
# =========================================================

OLLAMA_URL = (
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = "llama3.2:1b"


# =========================================================
# OLLAMA READINESS STATE
# =========================================================
#
# False:
#   Ollama/model has not yet been confirmed ready.
#
# True:
#   The model has successfully completed the warm-up
#   request and should already be loaded in memory.
#
# IMPORTANT:
#
# False does NOT mean Ollama is broken.
# It can simply mean that the model is still loading.
# =========================================================

OLLAMA_READY = False

OLLAMA_READY_LOCK = threading.Lock()


def set_ollama_ready(value):
    global OLLAMA_READY

    with OLLAMA_READY_LOCK:
        OLLAMA_READY = bool(value)


def is_ollama_ready():

    with OLLAMA_READY_LOCK:
        return OLLAMA_READY


# =========================================================
# OLLAMA BACKGROUND PRELOAD
# =========================================================
#
# The model is loaded in a background thread.
#
# FastAPI does NOT wait for the model during startup.
#
# This prevents a slow Ollama cold start from preventing
# the rest of the API from starting.
# =========================================================

def preload_ollama_model():

    print(
        "[OLLAMA] Starting background model preload...",
        flush=True
    )

    payload = {

        "model":
            OLLAMA_MODEL,

        "prompt":
            "Ready.",

        "stream":
            False,

        "keep_alive":
            "30m",

        "options": {

            "temperature":
                0,

            "num_predict":
                1,

            "num_ctx":
                2048
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,

            # This timeout applies only to the
            # background warm-up request.
            timeout=300
        )

        response.raise_for_status()

        set_ollama_ready(True)

        print(
            "[OLLAMA] llama3.2:1b loaded and ready.",
            flush=True
        )

    except requests.exceptions.Timeout:

        set_ollama_ready(False)

        print(
            "[OLLAMA] Background model preload timed out.",
            flush=True
        )

        print(
            "[OLLAMA] FastAPI will continue normally.",
            flush=True
        )

    except requests.exceptions.ConnectionError:

        set_ollama_ready(False)

        print(
            "[OLLAMA] Ollama is not running.",
            flush=True
        )

        print(
            "[OLLAMA] FastAPI will continue normally.",
            flush=True
        )

    except requests.exceptions.RequestException as error:

        set_ollama_ready(False)

        print(
            "[OLLAMA] Background preload failed:",
            repr(error),
            flush=True
        )

    except Exception as error:

        set_ollama_ready(False)

        print(
            "[OLLAMA] Unexpected preload error:",
            repr(error),
            flush=True
        )


# =========================================================
# START OLLAMA PRELOAD
# =========================================================

@app.on_event("startup")
def start_ollama_preload():

    print(
        "[OLLAMA] Starting model warm-up in background...",
        flush=True
    )

    thread = threading.Thread(
        target=preload_ollama_model,
        daemon=True
    )

    thread.start()


# =========================================================
# RAG RETRIEVAL SYSTEM PRELOAD
# =========================================================

@app.on_event("startup")
def preload_rag_system():

    print(
        "[RAG] Preloading retrieval system...",
        flush=True
    )

    try:

        from app.retrieval.hybrid_search import search

        search(
            "email",
            top_k=1
        )

        print(
            "[RAG] Retrieval system loaded and ready.",
            flush=True
        )

    except Exception as error:

        print(
            "[RAG] Retrieval preload failed. "
            "FastAPI will continue starting:",
            repr(error),
            flush=True
        )


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(
    websocket_router
)

app.include_router(
    query_router
)

app.include_router(
    hubs_router
)

app.include_router(
    entities_router
)

app.include_router(
    timeline_router
)

app.include_router(
    health_router
)

app.include_router(
    emails_router
)

app.include_router(
    insights_router
)

app.include_router(
    ingestion_router
)

app.include_router(
    risk_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message":
            "Enron Email Intelligence System API"
    }


# =========================================================
# DATABASE DEBUG
# =========================================================

@app.get("/debug/database")
def debug_database():

    from app.database.mongodb import (
        emails_collection
    )

    try:

        total = (
            emails_collection
            .estimated_document_count()
        )

        sample = (
            emails_collection.find_one(
                {},
                {
                    "_id": 0,
                    "message_id": 1,
                    "from": 1,
                    "to": 1,
                    "subject": 1
                }
            )
        )

        return {
            "database":
                "enron_email_intelligence",

            "collection":
                "emails",

            "total_emails":
                total,

            "sample":
                sample
        }

    except Exception as error:

        print(
            "[DEBUG/DATABASE] Error:",
            error
        )

        return {
            "database":
                "enron_email_intelligence",

            "collection":
                "emails",

            "error":
                str(error)
        }