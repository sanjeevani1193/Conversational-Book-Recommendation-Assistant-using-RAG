from src.embedder import load_embedding_model
from src.explainer import explain_recommendations
from src.pipeline import get_recommendations


def is_no_change(text: str) -> bool:
    no_change_values = {
        "",
        "no",
        "nope",
        "n",
        "none",
        "nothing",
        "nah",
        "no changes",
        "no more changes",
        "no other changes",
        "no extra preferences",
        "no preference changes",
        "no preferences"
    }
    return text.strip().lower() in no_change_values


def build_final_query(base_query: str, preferences: list[str]) -> str:
    if not preferences:
        return base_query
    return f"{base_query}. Extra preferences: {'; '.join(preferences)}"


def print_results(result: dict):
    print("\nRefined query:")
    print(result["parsed_query"])

    print("\nSearch queries:")
    for q in result["search_queries"]:
        print("-", q)

    stats = result["stats"]
    print(f"\nGoogle raw results collected: {stats['google_raw']}")
    print(f"Open Library raw results collected: {stats['openlibrary_raw']}")
    print(f"Retrieved before deduplication: {stats['all_books']}")
    print(f"Retrieved after deduplication: {stats['unique_books']}")
    print(f"Retrieved after enrichment + text-quality filtering: {stats['usable_books']}")

    print("\nTop 3 books:")
    for i, book in enumerate(result["top_books"], start=1):
        print(f"\n{i}. {book['title']} by {book['author']}")
        print(f"Semantic score: {book['similarity_score']:.4f}")
        print(f"Final score: {book['final_score']:.4f}")
        print(f"Primary hits: {book.get('primary_hits', 0)}")
        print(f"Secondary hits: {book.get('secondary_hits', 0)}")
        print(f"Must-have hits: {book.get('must_have_hits', 0)}")
        print(f"Vibe hits: {book.get('vibe_hits', 0)}")
        print(f"Avoid hits: {book.get('avoid_hits', 0)}")
        print(f"Source: {book['source']}")
        print(f"Categories: {book['categories']}")
        print(f"Published year: {book.get('published_year', '')}")
        print(f"ISBN: {book.get('isbn', '')}")
        print(f"Link: {book['info_link']}")

    print("\nExplanation:")
    print(result["explanation"])


def main():
    base_query = input("Enter your main book request: ").strip()
    preferences = []

    model = load_embedding_model()

    while True:
        user_query = build_final_query(base_query, preferences)
        print("\nOriginal query:")
        print(user_query)

        result = get_recommendations(
            user_query=user_query,
            model=model,
            explain_fn=explain_recommendations
        )

        print_results(result)

        followup = input(
            "\nAny extra preferences or changes? Type them, or type 'no' / press Enter if none: "
        ).strip()

        if is_no_change(followup):
            print("\nOkay, ending session.")
            break

        preferences.append(followup)


if __name__ == "__main__":
    main()