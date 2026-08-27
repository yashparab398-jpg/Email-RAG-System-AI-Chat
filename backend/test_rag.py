from pprint import pprint

from app.services.rag_service import answer_question


response = answer_question(
    "What emails discuss energy trading?"
)

pprint(response)