import ollama
from src.prompts import get_explanation_prompt


def explain_recommendations(user_query: str, top_books: list) -> str:
    prompt = get_explanation_prompt(user_query, top_books)

    response = ollama.chat(
        model="gemma3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]