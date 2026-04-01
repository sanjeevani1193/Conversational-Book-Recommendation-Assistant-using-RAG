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

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

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

    # Nonfiction / self-help / psychology / productivity
    if any(word in query for word in ["discipline", "self control", "self-control", "willpower"]):
        primary.extend(["self-discipline", "self-control", "habit building"])
        secondary.extend(["productivity", "behavior change", "personal development"])
        vibe.extend(["practical", "motivational", "actionable"])
        avoid.extend(["fiction", "romance"])

    if any(word in query for word in ["habit", "habits", "routine", "consistency"]):
        if "habit building" not in primary:
            primary.append("habit building")
        secondary.extend(["routines", "behavior change", "personal development"])
        vibe.extend(["practical", "actionable"])

    if any(word in query for word in ["productivity", "focus", "procrastination"]):
        primary.extend(["productivity", "focus", "time management"])
        secondary.extend(["motivation", "self-discipline", "personal development"])
        vibe.extend(["practical", "clear", "actionable"])
        avoid.extend(["fiction"])

    if any(word in query for word in ["psychology", "mindset", "mental health", "healing", "grief", "trauma"]):
        primary.extend(["psychology", "mental health", "personal growth"])
        secondary.extend(["healing", "mindset", "emotional wellbeing"])
        vibe.extend(["reflective", "thought-provoking", "emotional"])

    if any(word in query for word in ["business", "career", "leadership", "success"]):
        primary.extend(["business", "leadership", "career development"])
        secondary.extend(["decision making", "productivity", "personal development"])
        vibe.extend(["practical", "insightful"])

    if any(word in query for word in ["philosophy", "meaning", "purpose"]):
        primary.extend(["philosophy", "meaning of life", "self-reflection"])
        secondary.extend(["purpose", "human nature", "thought-provoking"])
        vibe.extend(["reflective", "deep"])

    if any(word in query for word in ["biography", "memoir", "life story"]):
        primary.extend(["biography", "memoir"])
        secondary.extend(["inspirational", "personal journey"])
        vibe.extend(["reflective", "emotional"])

    # Fiction
    if any(word in query for word in ["fantasy", "magic", "kingdom", "dragon"]):
        primary.append("fantasy")
        secondary.extend(["magic", "adventure"])
        vibe.extend(["immersive", "atmospheric"])

    if any(word in query for word in ["thriller", "suspense", "mystery", "crime"]):
        primary.extend(["thriller", "mystery"])
        secondary.extend(["suspense", "crime"])
        vibe.extend(["tense", "fast-paced"])

    if any(word in query for word in ["romance", "love story", "love"]):
        primary.append("romance")
        vibe.extend(["emotional", "character-driven"])

    if "enemies to lovers" in query:
        secondary.append("enemies to lovers")
        must_have.append("enemies to lovers")

    if "slow burn" in query:
        secondary.append("slow burn")
        vibe.append("slow burn")

    if any(word in query for word in ["dark", "darker tone", "dark tone"]):
        vibe.append("dark")

    def dedupe_keep_order(items):
        seen = set()
        output = []
        for item in items:
            cleaned = item.strip().lower()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                output.append(item)
        return output[:4]

    return {
        "primary_search_tags": dedupe_keep_order(primary),
        "secondary_search_tags": dedupe_keep_order(secondary),
        "vibe_tags": dedupe_keep_order(vibe),
        "must_have_tropes": dedupe_keep_order(must_have),
        "avoid_terms": dedupe_keep_order(avoid),
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
        normalized = normalize_parsed_query(parsed)

        # guardrail: if the model returns nothing useful, use fallback
        total_tags = sum(len(normalized[key]) for key in EXPECTED_KEYS)
        if total_tags == 0:
            return fallback_tag_parse(user_query)

        return normalized

    except json.JSONDecodeError:
        print("\nWarning: Ollama did not return clean JSON. Falling back to heuristic tags.")
        print(f"Raw Ollama output:\n{output_text}\n")
        return fallback_tag_parse(user_query)