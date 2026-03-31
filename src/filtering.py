def build_book_text(book: dict) -> str:
    return " ".join([
        book.get("title", ""),
        book.get("author", ""),
        book.get("categories", ""),
        book.get("description", "")
    ]).strip()


def looks_like_non_book_junk(book: dict) -> bool:
    title = (book.get("title", "") or "").lower()
    categories = (book.get("categories", "") or "").lower()

    blocked_terms = [
        "journal",
        "magazine",
        "newspaper",
        "review",
        "proceedings",
        "bulletin",
        "international journal"
    ]

    for term in blocked_terms:
        if term in title or term in categories:
            return True

    return False


def filter_books_with_usable_text(books: list, min_chars: int = 40) -> list:
    filtered = []

    for book in books:
        if looks_like_non_book_junk(book):
            continue

        text = build_book_text(book)
        if len(text) >= min_chars:
            filtered.append(book)

    return filtered