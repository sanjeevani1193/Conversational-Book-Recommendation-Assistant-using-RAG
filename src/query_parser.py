import json
import re
import ollama


def clean_llm_json_response(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return text.strip()


def rewrite_query_with_llm(user_query: str):
    prompt = f"""
Rewrite the following user query into structured search keywords for a book recommendation system.

Return ONLY raw JSON in this exact format:
{{
  "primary_keywords": ["keyword1", "keyword2"],
  "secondary_keywords": ["keyword3", "keyword4"],
  "broad_keywords": ["keyword5", "keyword6"]
}}

Do not use markdown.
Do not use triple backticks.
Do not add explanations.

User query: {user_query}
"""

    response = ollama.chat(
        model="gemma3",
        messages=[{"role": "user", "content": prompt}]
    )

    output_text = response["message"]["content"]
    output_text = clean_llm_json_response(output_text)

    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON returned by Ollama: {output_text}") from exc

    return parsed