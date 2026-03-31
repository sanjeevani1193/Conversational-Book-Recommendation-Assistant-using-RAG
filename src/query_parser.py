import json
import re
import ollama
from src.prompts import QUERY_REWRITE_SYSTEM_PROMPT


EXPECTED_KEYS = [
    "primary_search_tags",
    "secondary_search_tags",
    "vibe_tags",
    "must_have_tropes",
    "avoid_terms",
]


def clean_llm_json_response(text: str) -> str:
    text = text.strip()

    # Case 1: plain fenced JSON anywhere in the response
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    # Case 2: raw JSON object somewhere in the response
    json_match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if json_match:
        return json_match.group(0).strip()

    return text.strip()


def ensure_list_of_strings(value):
    if not isinstance(value, list):
        return []

    cleaned = []
    for item in value:
        if isinstance(item, str):
            item = item.strip()
            if item:
                cleaned.append(item)

    return cleaned[:4]


def normalize_parsed_query(parsed: dict) -> dict:
    normalized = {}

    for key in EXPECTED_KEYS:
        normalized[key] = ensure_list_of_strings(parsed.get(key, []))

    return normalized


def fallback_tag_parse(user_query: str) -> dict:
    query = user_query.lower()

    primary = []
    secondary = []
    vibe = []
    must_have = []
    avoid = []

    if "princess" in query or "prince" in query or "royal" in query:
        primary.append("royal romance")

    if "bodyguard" in query:
        primary.append("bodyguard romance")
        must_have.append("bodyguard")

    if "not allowed" in query or "forbidden" in query or "secret" in query:
        primary.append("forbidden romance")
        secondary.append("secret romance")
        must_have.append("forbidden love")

    if "love" in query:
        vibe.append("romantic tension")

    return {
        "primary_search_tags": primary[:4],
        "secondary_search_tags": secondary[:4],
        "vibe_tags": vibe[:4],
        "must_have_tropes": must_have[:4],
        "avoid_terms": avoid[:4],
    }


def rewrite_query_with_llm(user_query: str):
    response = ollama.chat(
        model="gemma3",
        messages=[
            {"role": "system", "content": QUERY_REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    output_text = response["message"]["content"]
    cleaned_text = clean_llm_json_response(output_text)

    try:
        parsed = json.loads(cleaned_text)
        return normalize_parsed_query(parsed)
    except json.JSONDecodeError:
        print("\nWarning: Ollama did not return clean JSON. Falling back to heuristic tags.")
        print(f"Raw Ollama output:\n{output_text}\n")
        return fallback_tag_parse(user_query)