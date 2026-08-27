from app.retrieval.hybrid_search import search


results = search(
    "energy forecast",
    top_k=5
)

print()

for result in results:
    print("-" * 80)
    print(result["from"])
    print(result["subject"])
    print(result["chunk_text"][:200])
    print()