from sklearn.metrics.pairwise import cosine_similarity


def rank_books_by_similarity(query_embedding, book_embeddings, books: list, top_k: int = 3) -> list:
    similarities = cosine_similarity([query_embedding], book_embeddings)[0]

    scored_books = []
    for book, score in zip(books, similarities):
        enriched_book = book.copy()
        enriched_book["similarity_score"] = float(score)
        scored_books.append(enriched_book)

    scored_books.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_books[:top_k]