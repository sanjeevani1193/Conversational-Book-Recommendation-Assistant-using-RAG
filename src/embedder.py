from sentence_transformers import SentenceTransformer


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)


def create_book_text(book: dict) -> str:
    return " ".join([
        book.get("title", ""),
        book.get("author", ""),
        book.get("categories", ""),
        book.get("description", "")
    ]).strip()


def embed_books(model, books: list):
    texts = [create_book_text(book) for book in books]
    return model.encode(texts, show_progress_bar=False)


def embed_query(model, query: str):
    return model.encode(query)