import re


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())
    return text


def normalize_isbn(isbn: str) -> str:
    isbn = (isbn or "").strip()
    isbn = isbn.replace("-", "").replace(" ", "")
    return isbn


def deduplicate_books(books: list) -> list:
    seen_isbns = set()
    seen_title_author = set()
    deduplicated = []

    for book in books:
        isbn = normalize_isbn(book.get("isbn", ""))
        title = normalize_text(book.get("title", ""))
        author = normalize_text(book.get("author", ""))
        title_author_key = (title, author)

        if isbn:
            if isbn in seen_isbns:
                continue
            seen_isbns.add(isbn)

            if title or author:
                seen_title_author.add(title_author_key)

            deduplicated.append(book)
            continue

        if title_author_key in seen_title_author:
            continue

        seen_title_author.add(title_author_key)
        deduplicated.append(book)

    return deduplicated