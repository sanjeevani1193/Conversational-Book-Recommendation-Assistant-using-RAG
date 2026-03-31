def extract_google_books_isbn(volume_info: dict) -> str:
    identifiers = volume_info.get("industryIdentifiers", []) or []

    for item in identifiers:
        id_type = item.get("type", "")
        identifier = item.get("identifier", "")

        if id_type in {"ISBN_13", "ISBN_10"} and identifier:
            return identifier.strip()

    return ""


def extract_google_books_year(volume_info: dict) -> str:
    published_date = volume_info.get("publishedDate", "") or ""
    return published_date[:4] if published_date else ""


def extract_google_books_language(volume_info: dict) -> str:
    return (volume_info.get("language") or "").strip()


def extract_google_books_cover(volume_info: dict) -> str:
    image_links = volume_info.get("imageLinks", {}) or {}
    return (
        image_links.get("thumbnail")
        or image_links.get("smallThumbnail")
        or ""
    ).strip()


def normalize_google_books(items: list) -> list:
    normalized = []

    for item in items:
        volume_info = item.get("volumeInfo", {})

        normalized.append({
            "title": (volume_info.get("title") or "").strip(),
            "author": ", ".join(volume_info.get("authors", [])) if volume_info.get("authors") else "",
            "description": (volume_info.get("description") or "").strip(),
            "categories": ", ".join(volume_info.get("categories", [])) if volume_info.get("categories") else "",
            "isbn": extract_google_books_isbn(volume_info),
            "published_year": extract_google_books_year(volume_info),
            "language": extract_google_books_language(volume_info),
            "cover_url": extract_google_books_cover(volume_info),
            "source": "google_books",
            "source_id": item.get("id", ""),
            "work_key": "",
            "info_link": (volume_info.get("infoLink") or "").strip()
        })

    return normalized


def extract_open_library_description(detail_item: dict) -> str:
    description = detail_item.get("description", "")

    if isinstance(description, str):
        return description.strip()

    if isinstance(description, dict):
        return (description.get("value") or "").strip()

    return ""


def extract_open_library_isbn(item: dict) -> str:
    isbn_list = item.get("isbn", []) or []
    return isbn_list[0].strip() if isbn_list else ""


def extract_open_library_year(item: dict) -> str:
    year = item.get("first_publish_year", "")
    return str(year).strip() if year else ""


def extract_open_library_language(item: dict) -> str:
    languages = item.get("language", []) or []
    return languages[0].strip() if languages else ""


def extract_open_library_cover(item: dict) -> str:
    cover_id = item.get("cover_i")
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    return ""


def normalize_open_library(items: list, detail_lookup: dict | None = None) -> list:
    detail_lookup = detail_lookup or {}
    normalized = []

    for item in items:
        work_key = item.get("key", "") or ""
        detail_item = detail_lookup.get(work_key, {})
        description = extract_open_library_description(detail_item) if detail_item else ""

        normalized.append({
            "title": (item.get("title") or "").strip(),
            "author": ", ".join(item.get("author_name", [])) if item.get("author_name") else "",
            "description": description,
            "categories": ", ".join(item.get("subject", [])) if item.get("subject") else "",
            "isbn": extract_open_library_isbn(item),
            "published_year": extract_open_library_year(item),
            "language": extract_open_library_language(item),
            "cover_url": extract_open_library_cover(item),
            "source": "open_library",
            "source_id": work_key,
            "work_key": work_key,
            "info_link": f"https://openlibrary.org{work_key}" if work_key else ""
        })

    return normalized