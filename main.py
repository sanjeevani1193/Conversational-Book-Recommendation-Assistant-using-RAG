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


def dedupe_list(items: list[str]) -> list[str]:
    seen = set()
    output = []

    for item in items:
        cleaned = clean_search_text((item or "").strip().lower())
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            output.append(cleaned)

    return output


def build_search_tag_groups(parsed_query: dict, user_query: str) -> dict:
    primary = dedupe_list(parsed_query.get("primary_search_tags", []))
    secondary = dedupe_list(parsed_query.get("secondary_search_tags", []))
    vibe = dedupe_list(parsed_query.get("vibe_tags", []))
    must_have_tropes = dedupe_list(parsed_query.get("must_have_tropes", []))
    avoid_terms = dedupe_list(parsed_query.get("avoid_terms", []))

    return {
        "primary": primary,
        "secondary": secondary,
        "vibe": vibe,
        "must_have_tropes": must_have_tropes,
        "avoid_terms": avoid_terms,
        "fallback": [clean_search_text(user_query)]
    }


def build_api_queries(tag_groups: dict) -> list[str]:
    primary = tag_groups["primary"]
    secondary = tag_groups["secondary"]
    fallback = tag_groups["fallback"]

    queries = []

    # strongest single retrieval terms
    queries.extend(primary[:3])

    # strongest combinations first
    if len(primary) >= 2:
        queries.append(f"{primary[0]} {primary[1]}")
    if len(primary) >= 3:
        queries.append(f"{primary[0]} {primary[2]}")
    if primary and secondary:
        queries.append(f"{primary[0]} {secondary[0]}")

    # only a light use of secondary tags
    queries.extend(secondary[:1])

    # fallback last
    queries.extend(fallback)

    return dedupe_list(queries)[:7]


def collect_google_results(search_queries: list[str], max_total: int = 10, per_query: int = 2) -> list:
    collected = []

    for query in search_queries:
        try:
            results = search_google_books(query, max_results=per_query)
            print(f"Google query: {query} -> {len(results)} results")
            collected.extend(results)
        except Exception as exc:
            print(f"Google query failed for '{query}': {exc}")

        if len(collected) >= max_total:
            break

    return collected[:max_total]


def collect_openlibrary_results(search_queries: list[str], max_total: int = 8, per_query: int = 2) -> list:
    collected = []

    # keep Open Library lighter
    for query in search_queries[:4]:
        try:
            results = search_open_library(query, limit=per_query)
            print(f"Open Library query: {query} -> {len(results)} results")
            collected.extend(results)
        except Exception as exc:
            print(f"Open Library query failed for '{query}': {exc}")

        if len(collected) >= max_total:
            break

    return collected[:max_total]


def enrich_open_library_books_with_descriptions(books: list, max_enrich: int = 4) -> list:
    enriched_books = []
    enrich_count = 0

    for book in books:
        if book.get("source") != "open_library":
            enriched_books.append(book)
            continue

        if enrich_count >= max_enrich:
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
            enrich_count += 1
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


def build_final_query(base_query: str, preferences: list[str]) -> str:
    if not preferences:
        return base_query
    return f"{base_query}. Extra preferences: {'; '.join(preferences)}"


def build_rerank_query(user_query: str, tag_groups: dict) -> str:
    parts = [user_query]

    if tag_groups["must_have_tropes"]:
        parts.append("Must-have tropes: " + ", ".join(tag_groups["must_have_tropes"]))

    if tag_groups["vibe"]:
        parts.append("Desired vibe: " + ", ".join(tag_groups["vibe"]))

    return " | ".join(parts)


def run_pipeline(user_query: str, model):
    print("\nOriginal query:")
    print(user_query)

    parsed_query = rewrite_query_with_llm(user_query)
    print("\nRefined query:")
    print(parsed_query)

    tag_groups = build_search_tag_groups(parsed_query, user_query)
    search_queries = build_api_queries(tag_groups)

    print("\nSearch queries:")
    for q in search_queries:
        print("-", q)

    google_raw = collect_google_results(search_queries, max_total=10, per_query=2)
    openlibrary_raw = collect_openlibrary_results(search_queries, max_total=8, per_query=2)

    print(f"\nGoogle raw results collected: {len(google_raw)}")
    print(f"Open Library raw results collected: {len(openlibrary_raw)}")

    google_books = normalize_google_books(google_raw)
    openlibrary_books = normalize_open_library(openlibrary_raw, detail_lookup={})

    print(f"Google normalized books: {len(google_books)}")
    print(f"Open Library normalized books: {len(openlibrary_books)}")

    all_books = google_books + openlibrary_books
    unique_books = deduplicate_books(all_books)

    enriched_unique_books = enrich_open_library_books_with_descriptions(unique_books, max_enrich=4)
    usable_books = filter_books_with_usable_text(enriched_unique_books)

    print(f"\nRetrieved before deduplication: {len(all_books)}")
    print(f"Retrieved after deduplication: {len(unique_books)}")
    print(f"Retrieved after enrichment + text-quality filtering: {len(usable_books)}")

    if not usable_books:
        print("No usable books found.")
        return

    book_embeddings = embed_books(model, usable_books)
    rerank_query = build_rerank_query(user_query, tag_groups)
    query_embedding = embed_query(model, rerank_query)

    top_books = rank_books_by_similarity(
        query_embedding=query_embedding,
        book_embeddings=book_embeddings,
        books=usable_books,
        top_k=3,
        primary_tags=tag_groups["primary"],
        secondary_tags=tag_groups["secondary"],
        must_have_tropes=tag_groups["must_have_tropes"],
        vibe_tags=tag_groups["vibe"],
        avoid_terms=tag_groups["avoid_terms"]
    )

    print("\nTop 3 books:")
    for i, book in enumerate(top_books, start=1):
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

    explanation = explain_recommendations(user_query, top_books)

    print("\nExplanation:")
    print(explanation)


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