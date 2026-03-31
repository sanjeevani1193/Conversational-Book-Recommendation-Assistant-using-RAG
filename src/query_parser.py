import json
import re
import ollama
from src.prompts import QUERY_REWRITE_SYSTEM_PROMPT


def clean_llm_json_response(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return text.strip()


def rewrite_query_with_llm(user_query: str):
    response = ollama.chat(
        model="gemma3",
        messages=[
            {"role": "system", "content": QUERY_REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    output_text = response["message"]["content"]
    output_text = clean_llm_json_response(output_text)

    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON returned by Ollama: {output_text}") from exc

    return parsed