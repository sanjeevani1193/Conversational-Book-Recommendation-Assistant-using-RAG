from sklearn.metrics.pairwise import cosine_similarity


def safe_text(book: dict) -> str:
    return " ".join([
        book.get("title", ""),
        book.get("author", ""),
        book.get("categories", ""),
        book.get("description", "")
    ]).lower()


def count_matches(text: str, terms: list[str]) -> int:
    matches = 0
    for term in terms:
        term = (term or "").strip().lower()
        if term and term in text:
            matches += 1
    return matches


def rank_books_by_similarity(
    query_embedding,
    book_embeddings,
    books: list,
    top_k: int = 3,
    primary_tags: list[str] | None = None,
    secondary_tags: list[str] | None = None,
    must_have_tropes: list[str] | None = None,
    vibe_tags: list[str] | None = None,
    avoid_terms: list[str] | None = None
) -> list:
    primary_tags = primary_tags or []
    secondary_tags = secondary_tags or []
    must_have_tropes = must_have_tropes or []
    vibe_tags = vibe_tags or []
    avoid_terms = avoid_terms or []

    similarities = cosine_similarity([query_embedding], book_embeddings)[0]

    scored_books = []
    for book, semantic_score in zip(books, similarities):
        text = safe_text(book)

        primary_hits = count_matches(text, primary_tags)
        secondary_hits = count_matches(text, secondary_tags)
        must_have_hits = count_matches(text, must_have_tropes)
        vibe_hits = count_matches(text, vibe_tags)
        avoid_hits = count_matches(text, avoid_terms)

        final_score = float(semantic_score)
        final_score += 0.05 * primary_hits
        final_score += 0.03 * secondary_hits
        final_score += 0.06 * must_have_hits
        final_score += 0.015 * vibe_hits
        final_score -= 0.06 * avoid_hits

        enriched_book = book.copy()
        enriched_book["similarity_score"] = float(semantic_score)
        enriched_book["final_score"] = final_score
        enriched_book["primary_hits"] = primary_hits
        enriched_book["secondary_hits"] = secondary_hits
        enriched_book["must_have_hits"] = must_have_hits
        enriched_book["vibe_hits"] = vibe_hits
        enriched_book["avoid_hits"] = avoid_hits

        scored_books.append(enriched_book)

    scored_books.sort(key=lambda x: x["final_score"], reverse=True)
    return scored_books[:top_k]