from bson import ObjectId

from app.retrieval.hybrid_search import search
from app.database.mongodb import emails_collection
from app.services.llm_service import generate_answer


def answer_question(
    question,
    top_k=5
):

    # ---------------------------------------------------------
    # RETRIEVE
    # ---------------------------------------------------------

    results = search(
        question,
        top_k=top_k
    )

    if not results:

        return {
            "answer":
                "No matching emails were found.",

            "confidence":
                0,

            "sources":
                []
        }

    # ---------------------------------------------------------
    # KEEP ONLY RELEVANT RETRIEVAL RESULTS
    # ---------------------------------------------------------
    #
    # Strong evidence is >= 0.50.
    #
    # We also keep the single best result even if its score
    # happens to be slightly below the threshold.
    # ---------------------------------------------------------

    strong_results = [
        result
        for result in results
        if float(
            result.get(
                "_retrieval_score",
                0
            )
        ) >= 0.50
    ]

    if not strong_results:

        strong_results = results[:1]

    # Never send more than 3 pieces of evidence.

    strong_results = strong_results[:3]

    # ---------------------------------------------------------
    # GET EMAILS FROM MONGODB
    # ---------------------------------------------------------

    email_map = {}

    for result in strong_results:

        email_id = result.get(
            "email_id"
        )

        if not email_id:
            continue

        try:

            email = emails_collection.find_one(
                {
                    "_id":
                        ObjectId(
                            email_id
                        )
                },
                {
                    "raw_body":
                        0
                }
            )

        except Exception:

            continue

        if not email:
            continue

        email["_id"] = str(
            email["_id"]
        )

        email_map[
            email["_id"]
        ] = email

    sources = list(
        email_map.values()
    )

    if not sources:

        return {
            "answer":
                "No matching emails were found.",

            "confidence":
                0,

            "sources":
                []
        }

    # ---------------------------------------------------------
    # GENERATE ANSWER
    # ---------------------------------------------------------

    llm_result = generate_answer(
        question,
        sources
    )

    # ---------------------------------------------------------
    # HANDLE LLM FAILURE
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Do not calculate an 80/90/95% confidence score when
    # Ollama failed to generate an answer.
    # ---------------------------------------------------------

    if isinstance(
        llm_result,
        dict
    ):

        answer = str(
            llm_result.get(
                "answer",
                ""
            )
        )

        llm_success = bool(
            llm_result.get(
                "success",
                False
            )
        )

    else:

        # Backwards compatibility in case generate_answer()
        # is temporarily replaced by an older implementation.

        answer = str(
            llm_result
            or ""
        )

        llm_success = True

    # ---------------------------------------------------------
    # LLM FAILURE
    # ---------------------------------------------------------

    if not llm_success:

        return {
            "answer":
                answer,

            "confidence":
                0,

            "sources":
                sources
        }

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------

    best_score = max(
        float(
            result.get(
                "_retrieval_score",
                0
            )
        )
        for result in strong_results
    )

    # Convert retrieval strength into a conservative
    # user-facing confidence.

    if best_score >= 0.75:

        confidence = 95

    elif best_score >= 0.60:

        confidence = 90

    elif best_score >= 0.50:

        confidence = 80

    elif best_score >= 0.40:

        confidence = 65

    else:

        confidence = 50

    # ---------------------------------------------------------
    # LOWER CONFIDENCE IF MODEL SAYS EVIDENCE IS INSUFFICIENT
    # ---------------------------------------------------------

    insufficient_phrases = [

        "provided evidence is insufficient",

        "evidence is insufficient",

        "does not answer the question",

        "does not contain enough information",

        "cannot be determined",

        "not enough information",

        "unable to determine",

        "cannot answer",

        "does not provide enough information"
    ]

    answer_lower = answer.lower()

    if any(
        phrase in answer_lower
        for phrase in insufficient_phrases
    ):

        confidence = 15

    # ---------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------

    return {
        "answer":
            answer,

        "confidence":
            round(
                confidence,
                2
            ),

        "sources":
            sources
    }