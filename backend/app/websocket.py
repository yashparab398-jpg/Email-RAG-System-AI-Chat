import json
import asyncio

from asyncio import to_thread

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.services.rag_service import answer_question


router = APIRouter()


# =========================================================
# CHAT SESSION STORAGE
# =========================================================

sessions = {}


MAX_HISTORY = 10


# =========================================================
# OLLAMA READINESS CONFIGURATION
# =========================================================
#
# The Ollama model is loaded by main.py in the background.
#
# If the user asks a question while the model is still
# loading, Chat waits here instead of immediately sending
# the request to Ollama.
#
# This is the cold-start protection.
# =========================================================

OLLAMA_WAIT_TIMEOUT = 90

OLLAMA_CHECK_INTERVAL = 0.5


# =========================================================
# SESSION HISTORY
# =========================================================

def get_session_history(session_id):

    if session_id not in sessions:

        sessions[session_id] = []

    return sessions[session_id]


def add_to_history(
    session_id,
    role,
    content
):

    history = get_session_history(
        session_id
    )

    history.append(
        {
            "role":
                role,

            "content":
                content,
        }
    )

    if len(history) > MAX_HISTORY:

        del history[
            :-MAX_HISTORY
        ]


# =========================================================
# SAFE SESSION ID
# =========================================================

def normalize_session_id(session_id):

    if not session_id:

        return "anonymous"

    return str(
        session_id
    )[:100]


# =========================================================
# OLLAMA READINESS CHECK
# =========================================================

def get_ollama_ready_function():

    """
    Import the readiness function only when needed.

    This avoids creating unnecessary import coupling
    during module startup.
    """

    from app.main import is_ollama_ready

    return is_ollama_ready


async def wait_for_ollama():

    """
    Wait for the background Ollama warm-up to finish.

    Returns:

        True
            Ollama became ready.

        False
            Ollama did not become ready within the
            controlled waiting period.
    """

    try:

        is_ollama_ready = get_ollama_ready_function()

    except Exception as error:

        print(
            "[WS] Could not access Ollama readiness state:",
            repr(error),
            flush=True
        )

        return False


    # =====================================================
    # ALREADY READY
    # =====================================================

    if is_ollama_ready():

        return True


    print(
        "[WS] Ollama is still warming up. "
        "Waiting for model readiness...",
        flush=True
    )


    # =====================================================
    # WAIT FOR BACKGROUND PRELOAD
    # =====================================================

    start_time = asyncio.get_running_loop().time()


    while True:

        if is_ollama_ready():

            elapsed = (
                asyncio.get_running_loop().time()
                - start_time
            )

            print(
                "[WS] Ollama became ready after "
                f"{elapsed:.1f} seconds.",
                flush=True
            )

            return True


        elapsed = (
            asyncio.get_running_loop().time()
            - start_time
        )


        if elapsed >= OLLAMA_WAIT_TIMEOUT:

            print(
                "[WS] Ollama did not become ready "
                "within the allowed wait period.",
                flush=True
            )

            return False


        await asyncio.sleep(
            OLLAMA_CHECK_INTERVAL
        )


# =========================================================
# WEBSOCKET CHAT
# =========================================================

@router.websocket("/chat")
async def chat(
    websocket: WebSocket
):

    await websocket.accept()

    session_id = "anonymous"


    print(
        "[WS] Client connected.",
        flush=True
    )


    try:

        while True:

            # =================================================
            # RECEIVE MESSAGE
            # =================================================

            raw_message = (
                await websocket.receive_text()
            )


            # =================================================
            # PARSE MESSAGE
            # =================================================

            try:

                payload = json.loads(
                    raw_message
                )

            except json.JSONDecodeError:

                payload = {
                    "type":
                        "user_message",

                    "message":
                        raw_message,
                }


            # =================================================
            # MESSAGE TYPE
            # =================================================

            message_type = payload.get(
                "type",
                "user_message"
            )


            if message_type != "user_message":

                await websocket.send_json(
                    {
                        "type":
                            "error",

                        "message":
                            "Unsupported WebSocket message type.",
                    }
                )

                continue


            # =================================================
            # SESSION
            # =================================================

            session_id = normalize_session_id(
                payload.get(
                    "session_id"
                )
            )


            # =================================================
            # QUESTION
            # =================================================

            question = str(
                payload.get(
                    "message",
                    ""
                )
            ).strip()


            if not question:

                await websocket.send_json(
                    {
                        "type":
                            "error",

                        "session_id":
                            session_id,

                        "message":
                            "Question cannot be empty.",
                    }
                )

                continue


            # =================================================
            # TOP K
            # =================================================

            try:

                top_k = int(
                    payload.get(
                        "top_k",
                        5
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                top_k = 5


            top_k = max(
                1,
                min(
                    top_k,
                    10
                )
            )


            # =================================================
            # SAVE USER MESSAGE
            # =================================================

            add_to_history(
                session_id,
                "user",
                question
            )


            print(
                f"[WS] Session={session_id} "
                f"Question={question}",
                flush=True
            )


            # =================================================
            # RETRIEVAL STARTED
            # =================================================

            await websocket.send_json(
                {
                    "type":
                        "retrieval_started",

                    "session_id":
                        session_id,
                }
            )


            # =================================================
            # WAIT FOR OLLAMA COLD START
            # =================================================
            #
            # IMPORTANT:
            #
            # This happens BEFORE answer_question().
            #
            # Therefore the first question does not compete
            # with the background model preload.
            # =================================================

            ollama_ready = await wait_for_ollama()


            if not ollama_ready:

                await websocket.send_json(
                    {
                        "type":
                            "assistant_token",

                        "session_id":
                            session_id,

                        "question":
                            question,

                        "content":
                            "The AI model is still starting. "
                            "Please try again in a moment.",

                        "answer":
                            "The AI model is still starting. "
                            "Please try again in a moment.",

                        "confidence":
                            0,

                        "sources":
                            [],
                    }
                )


                await websocket.send_json(
                    {
                        "type":
                            "assistant_done",

                        "session_id":
                            session_id,
                    }
                )


                print(
                    f"[WS] Session={session_id} "
                    "Ollama was not ready.",
                    flush=True
                )

                continue


            # =================================================
            # RUN RAG
            # =================================================
            #
            # answer_question() is synchronous.
            #
            # It performs:
            #
            # MongoDB
            # BM25
            # FAISS
            # Ollama
            #
            # Run it in a worker thread so the FastAPI
            # event loop remains responsive.
            # =================================================

            try:

                print(
                    "[WS] Starting answer_question...",
                    flush=True
                )


                response = await to_thread(
                    answer_question,
                    question,
                    top_k
                )


                print(
                    "[WS] answer_question() returned.",
                    flush=True
                )


            except Exception as error:

                print(
                    "[WS] RAG error:",
                    repr(error),
                    flush=True
                )


                await websocket.send_json(
                    {
                        "type":
                            "error",

                        "session_id":
                            session_id,

                        "message":
                            "Unable to process the question.",
                    }
                )

                continue


            # =================================================
            # RESPONSE DATA
            # =================================================

            answer = str(
                response.get(
                    "answer",
                    ""
                )
            )


            confidence = response.get(
                "confidence",
                0
            )


            sources = response.get(
                "sources",
                []
            )


            if not isinstance(
                sources,
                list
            ):

                sources = []


            # =================================================
            # SOURCE EVENTS
            # =================================================

            for source in sources[:5]:

                try:

                    await websocket.send_json(
                        {
                            "type":
                                "source_found",

                            "session_id":
                                session_id,

                            "email":
                                source,
                        }
                    )

                except Exception as error:

                    print(
                        "[WS] Source event error:",
                        repr(error),
                        flush=True
                    )

                    break


            # =================================================
            # ASSISTANT RESPONSE
            # =================================================

            await websocket.send_json(
                {
                    "type":
                        "assistant_token",

                    "session_id":
                        session_id,

                    "question":
                        question,

                    "content":
                        answer,

                    "answer":
                        answer,

                    "confidence":
                        confidence,

                    "sources":
                        sources,
                }
            )


            # =================================================
            # SAVE ASSISTANT RESPONSE
            # =================================================

            add_to_history(
                session_id,
                "assistant",
                answer
            )


            # =================================================
            # ASSISTANT DONE
            # =================================================

            await websocket.send_json(
                {
                    "type":
                        "assistant_done",

                    "session_id":
                        session_id,
                }
            )


            print(
                f"[WS] Session={session_id} "
                "Answer completed.",
                flush=True
            )


    # =========================================================
    # CLIENT DISCONNECT
    # =========================================================

    except WebSocketDisconnect:

        print(
            f"[WS] Client disconnected. "
            f"Session={session_id}",
            flush=True
        )


    # =========================================================
    # UNEXPECTED ERROR
    # =========================================================

    except Exception as error:

        print(
            "[WS] Unexpected error:",
            repr(error),
            flush=True
        )


        try:

            await websocket.send_json(
                {
                    "type":
                        "error",

                    "session_id":
                        session_id,

                    "message":
                        "The WebSocket encountered an unexpected error.",
                }
            )

        except Exception:

            pass