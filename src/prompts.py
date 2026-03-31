QUERY_REWRITE_SYSTEM_PROMPT = """
You are helping a conversational book recommendation assistant system.

Your task is to convert a user's natural-language request into search tags
that are likely to return relevant books from book APIs like Google Books
and Open Library.

Return ONLY valid JSON in this exact format:
{
  "must_have_tags": ["...", "..."],
  "nice_to_have_tags": ["...", "..."],
  "broad_tags": ["...", "..."]
}

Rules:
- Tags must be short and searchable.
- Prefer 1 to 3 words per tag.
- Focus on genre, trope, tone, theme, mood, character type, or relationship dynamic.
- Avoid long descriptive phrases.
- Avoid full sentences.
- Avoid explanations.
- Do not include markdown.
- Do not invent book titles or authors.
- Use at most 3 tags per list.
"""

def get_explanation_prompt(user_query: str, top_books: list) -> str:
    books_text = "\n".join(
        [
            f"- {book.get('title', 'Unknown Title')} by {book.get('author', 'Unknown Author')}\n"
            f"  Description: {book.get('description', '')}\n"
            f"  Categories: {book.get('categories', '')}"
            for book in top_books
        ]
    )

    return f"""
You are a helpful book recommendation assistant.

The user asked:
{user_query}

These are the top retrieved books:
{books_text}

Explain clearly and naturally why these books match the user's request.
Focus on tone, themes, tropes, emotional depth, relationship dynamics, and genre fit where relevant.
Keep it concise but useful.
"""