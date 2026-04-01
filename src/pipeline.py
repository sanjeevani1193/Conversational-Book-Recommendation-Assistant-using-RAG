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
from src.embedder import embed_books, embed_query
from src.ranker import rank_books_by_similarity

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

    queries.extend(primary[:3])

    if len(primary) >= 2:
        queries.append(f"{primary[0]} {primary[1]}")
    if len(primary) >= 3:
        queries.append(f"{primary[0]} {primary[2]}")
    if primary and secondary:
        queries.append(f"{primary[0]} {secondary[0]}")

    queries.extend(secondary[:1])
    queries.extend(fallback)

    return dedupe_list(queries)[:7]


def collect_google_results(search_queries: list[str], max_total: int = 10, per_query: int = 2) -> list:
    collected = []

    for query in search_queries:
        try:
            results = search_google_books(query, max_results=per_query)
            collected.extend(results)
        except Exception as exc:
            print(f"Google query failed for '{query}': {exc}")

        if len(collected) >= max_total:
            break

    return collected[:max_total]


def collect_openlibrary_results(search_queries: list[str], max_total: int = 8, per_query: int = 2) -> list:
    collected = []

    for query in search_queries[:4]:
        try:
            results = search_open_library(query, limit=per_query)
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


def build_rerank_query(user_query: str, tag_groups: dict) -> str:
    parts = [user_query]

    if tag_groups["must_have_tropes"]:
        parts.append("Must-have tropes: " + ", ".join(tag_groups["must_have_tropes"]))

    if tag_groups["vibe"]:
        parts.append("Desired vibe: " + ", ".join(tag_groups["vibe"]))

    return " | ".join(parts)


def get_recommendations(user_query: str, model, explain_fn) -> dict:
    parsed_query = rewrite_query_with_llm(user_query)
    tag_groups = build_search_tag_groups(parsed_query, user_query)
    search_queries = build_api_queries(tag_groups)

    google_raw = collect_google_results(search_queries, max_total=10, per_query=2)
    openlibrary_raw = collect_openlibrary_results(search_queries, max_total=8, per_query=2)

    google_books = normalize_google_books(google_raw)
    openlibrary_books = normalize_open_library(openlibrary_raw, detail_lookup={})

    all_books = google_books + openlibrary_books
    unique_books = deduplicate_books(all_books)

    enriched_unique_books = enrich_open_library_books_with_descriptions(unique_books, max_enrich=4)
    usable_books = filter_books_with_usable_text(enriched_unique_books)

    if not usable_books:
        return {
            "parsed_query": parsed_query,
            "tag_groups": tag_groups,
            "search_queries": search_queries,
            "top_books": [],
            "explanation": "No usable books found.",
            "stats": {
                "google_raw": len(google_raw),
                "openlibrary_raw": len(openlibrary_raw),
                "all_books": len(all_books),
                "unique_books": len(unique_books),
                "usable_books": 0
            }
        }

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

    explanation = explain_fn(user_query, top_books)

    return {
        "parsed_query": parsed_query,
        "tag_groups": tag_groups,
        "search_queries": search_queries,
        "top_books": top_books,
        "explanation": explanation,
        "stats": {
            "google_raw": len(google_raw),
            "openlibrary_raw": len(openlibrary_raw),
            "all_books": len(all_books),
            "unique_books": len(unique_books),
            "usable_books": len(usable_books)
        }
    }