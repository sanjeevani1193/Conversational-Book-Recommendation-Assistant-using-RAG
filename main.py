from src.query_parser import rewrite_query_with_llm
from src.api_clients import (
    search_google_books,
    search_open_library,
    get_open_library_work_details
)
from src.normalizer import (
    normalize_google_books,
    normalize_open_library,
    extract_open_library_description
)
from src.deduplicator import deduplicate_books
from src.filtering import filter_books_with_usable_text
from src.embedder import load_embedding_model, embed_books, embed_query
from src.ranker import rank_books_by_similarity
from src.explainer import explain_recommendations

import unicodedata

def clean_search_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.split())

def build_search_text(parsed_query: dict) -> str:
    return " ".join(
        parsed_query.get("primary_keywords", []) +
        parsed_query.get("secondary_keywords", []) +
        parsed_query.get("broad_keywords", [])
    )


def enrich_open_library_books_with_descriptions(books: list) -> list:
    enriched_books = []

    for book in books:
        if book.get("source") != "open_library":
            enriched_books.append(book)
            continue

        work_key = book.get("work_key", "")
        if not work_key:
            enriched_books.append(book)
            continue

        try:
            detail_item = get_open_library_work_details(work_key)
            description = extract_open_library_description(detail_item)

            enriched_book = book.copy()
            if description:
                enriched_book["description"] = description

            enriched_books.append(enriched_book)
        except Exception:
            enriched_books.append(book)

    return enriched_books

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


def ask_user_query() -> str:
    base_query = input("Enter your main book request: ").strip()
    extra_pref = input("Any extra preferences or changes? Type 'no' or press Enter if none: ").strip()

    if is_no_change(extra_pref):
        return base_query

    return f"{base_query}. Extra preferences: {extra_pref}"


def ask_followup_preference(current_query: str) -> str | None:
    followup = input(
        "\nAny changes to your preferences? Type them, or type 'no' / press Enter to keep this result: "
    ).strip()

    if is_no_change(followup):
        return None

    return f"{current_query}. Additional preference changes: {followup}"

def build_final_query(base_query: str, preferences: list[str]) -> str:
    if not preferences:
        return base_query
    return f"{base_query}. Extra preferences: {'; '.join(preferences)}"

def run_pipeline(user_query: str, model):
    print("\nOriginal query:")
    print(user_query)

    parsed_query = rewrite_query_with_llm(user_query)
    print("\nRefined query:")
    print(parsed_query)

    search_text = clean_search_text(build_search_text(parsed_query))
    print("\nSearch text:")
    print(search_text)

    google_raw = search_google_books(search_text, max_results=5)
    openlibrary_raw = search_open_library(search_text, limit=5)

    google_books = normalize_google_books(google_raw)
    openlibrary_books = normalize_open_library(openlibrary_raw, detail_lookup={})

    all_books = google_books + openlibrary_books
    unique_books = deduplicate_books(all_books)

    enriched_unique_books = enrich_open_library_books_with_descriptions(unique_books)
    usable_books = filter_books_with_usable_text(enriched_unique_books)

    print(f"\nRetrieved before deduplication: {len(all_books)}")
    print(f"Retrieved after deduplication: {len(unique_books)}")
    print(f"Retrieved after enrichment + text-quality filtering: {len(usable_books)}")

    if not usable_books:
        print("No usable books found.")
        return

    # model = load_embedding_model()

    book_embeddings = embed_books(model, usable_books)
    query_embedding = embed_query(model, user_query)

    top_books = rank_books_by_similarity(
        query_embedding=query_embedding,
        book_embeddings=book_embeddings,
        books=usable_books,
        top_k=3
    )

    print("\nTop 3 books:")
    for i, book in enumerate(top_books, start=1):
        print(f"\n{i}. {book['title']} by {book['author']}")
        print(f"Score: {book['similarity_score']:.4f}")
        print(f"Source: {book['source']}")
        print(f"Categories: {book['categories']}")
        print(f"Published year: {book.get('published_year', '')}")
        print(f"ISBN: {book.get('isbn', '')}")
        print(f"Link: {book['info_link']}")

    explanation = explain_recommendations(user_query, top_books)

    print("\nExplanation:")
    print(explanation)


# def main():
#     user_query = input("Enter your book request: ").strip()

#     print("\nOriginal query:")
#     print(user_query)

#     parsed_query = rewrite_query_with_llm(user_query)
#     print("\nRefined query:")
#     print(parsed_query)

#     # search_text = build_search_text(parsed_query)
#     search_text = clean_search_text(build_search_text(parsed_query))
#     print("\nSearch text:")
#     print(search_text)

#     google_raw = search_google_books(search_text, max_results=5)
#     openlibrary_raw = search_open_library(search_text, limit=5)

#     google_books = normalize_google_books(google_raw)

#     # lightweight Open Library normalization first, without detail enrichment
#     openlibrary_books = normalize_open_library(openlibrary_raw, detail_lookup={})

#     all_books = google_books + openlibrary_books
#     unique_books = deduplicate_books(all_books)

#     # enrich only surviving Open Library books after deduplication
#     enriched_unique_books = enrich_open_library_books_with_descriptions(unique_books)

#     usable_books = filter_books_with_usable_text(enriched_unique_books)

#     print(f"\nRetrieved before deduplication: {len(all_books)}")
#     print(f"Retrieved after deduplication: {len(unique_books)}")
#     print(f"Retrieved after enrichment + text-quality filtering: {len(usable_books)}")

#     if not usable_books:
#         print("No usable books found.")
#         return

#     model = load_embedding_model()

#     book_embeddings = embed_books(model, usable_books)
#     query_embedding = embed_query(model, user_query)

#     top_books = rank_books_by_similarity(
#         query_embedding=query_embedding,
#         book_embeddings=book_embeddings,
#         books=usable_books,
#         top_k=3
#     )

#     print("\nTop 3 books:")
#     for i, book in enumerate(top_books, start=1):
#         print(f"\n{i}. {book['title']} by {book['author']}")
#         print(f"Score: {book['similarity_score']:.4f}")
#         print(f"Source: {book['source']}")
#         print(f"Categories: {book['categories']}")
#         print(f"Published year: {book.get('published_year', '')}")
#         print(f"ISBN: {book.get('isbn', '')}")
#         print(f"Link: {book['info_link']}")

#     explanation = explain_recommendations(user_query, top_books)

#     print("\nExplanation:")
#     print(explanation)

def main():
    base_query = input("Enter your main book request: ").strip()
    preferences = []

    model = load_embedding_model()

    while True:
        user_query = build_final_query(base_query, preferences)
        run_pipeline(user_query, model)

        followup = input(
            "\nAny extra preferences or changes? Type them, or type 'no' / press Enter if none: "
        ).strip()

        if is_no_change(followup):
            print("\nOkay, ending session.")
            break

        preferences.append(followup)


if __name__ == "__main__":
    main()