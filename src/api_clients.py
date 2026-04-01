import os
import time
import requests
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

OPENLIB_HEADERS = {
    "User-Agent": "BookRAG (your_email@example.com)"
}

session = requests.Session()
session.headers.update(OPENLIB_HEADERS)

_LAST_OL_REQUEST_TIME = 0.0
MIN_OL_INTERVAL = 0.40  # safely below 3 req/sec


def throttled_openlibrary_get(url: str, params: Optional[dict] = None) -> dict:
    global _LAST_OL_REQUEST_TIME

    now = time.time()
    elapsed = now - _LAST_OL_REQUEST_TIME
    if elapsed < MIN_OL_INTERVAL:
        time.sleep(MIN_OL_INTERVAL - elapsed)

    response = session.get(url, params=params, timeout=20)
    _LAST_OL_REQUEST_TIME = time.time()
    response.raise_for_status()
    return response.json()


def search_google_books(query: str, max_results: int = 5, retries: int = 4) -> list:
    if not GOOGLE_BOOKS_API_KEY:
        raise ValueError("Missing GOOGLE_BOOKS_API_KEY in .env")

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": GOOGLE_BOOKS_API_KEY
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=20)

            if response.status_code in {500, 502, 503, 504}:
                if attempt == retries - 1:
                    response.raise_for_status()

                wait_time = 2 ** attempt
                print(f"Google Books temporary error {response.status_code}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            return data.get("items", [])

        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise

            wait_time = 2 ** attempt
            print(f"Google Books request failed. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    return []


def search_open_library(query: str, limit: int = 5) -> list:
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": limit}
    data = throttled_openlibrary_get(url, params=params)
    return data.get("docs", [])


def get_open_library_work_details(work_key: str) -> dict:
    if not work_key:
        return {}

    url = f"https://openlibrary.org{work_key}.json"
    return throttled_openlibrary_get(url)