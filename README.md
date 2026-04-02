# Conversational Book Recommendation Assistant using RAG

A conversational book recommendation system that converts natural-language reading preferences into relevant book suggestions using a Retrieval-Augmented Generation (RAG) pipeline.

Instead of relying solely on a language model to generate recommendations, this project uses a structured workflow: interpret the user's request → generate focused retrieval tags → fetch books from external sources → clean and enrich metadata → rank and present final recommendations.

---

## Overview

Users often describe the books they want in a natural, conversational way rather than with clean search keywords. Examples:

- *"I want books that help me become more disciplined"*
- *"Recommend fantasy books with political intrigue and morally grey characters"*
- *"I want an emotional romance but not something toxic"*
- *"Suggest comforting books for a reading slump"*

Public book APIs don't handle these long, messy queries well. This project addresses that by first converting the user's prompt into retrieval-friendly tags, then using those tags to fetch and rank candidate books.

---

## Motivation

Traditional search-based recommendation performs poorly when users express preferences conversationally. A long natural-language request can be too broad, too specific, too noisy, or poorly suited for direct API retrieval.

This project solves that by combining:
- LLM-based query understanding
- External retrieval from book APIs
- Preprocessing and deduplication
- Relevance-based ranking
- An interactive Streamlit interface

It demonstrates practical skills in NLP, retrieval, data processing, and application development.

---

## How the System Works

### 1. User enters a request
The user describes the type of book they're looking for in natural language.

> *"I want a motivating self-help book that helps me become more disciplined and improve my habits."*

### 2. Tags are generated
The LLM extracts focused, atomic retrieval tags from the request rather than using the full query directly.

Example generated tags: `discipline`, `habits`, `self-help`, `productivity`, `motivation`, `personal growth`

### 3. Candidate books are retrieved
Each tag is used to search external sources independently:
- **Google Books API**
- **Open Library API**

### 4. Results are cleaned and standardized
Returned book data is normalized across sources, covering fields like title, authors, description, categories, ratings, and identifiers.

### 5. Duplicates are removed
Books retrieved from multiple APIs are deduplicated.

### 6. Metadata is enriched
Missing fields are supplemented using merged API results where possible.

### 7. Books are ranked
Candidates are scored and ranked based on relevance to the generated tags and metadata quality.

### 8. Recommendations are displayed
The user receives a curated list of book recommendations through the Streamlit interface.

---

## Tech Stack

| Component | Tool |
|---|---|
| Language | Python |
| UI | Streamlit |
| Local LLM | Ollama (Gemma3) |
| Book Sources | Google Books API, Open Library API |
| Data Processing | Pandas |
| HTTP Requests | Requests |

---

## Project Structure
```
Conversational-Book-Recommendation-Assistant-using-RAG/
│
├── app/
│   └── app.py
│
├── src/
│   ├── __init__.py
│   ├── api_clients.py
│   ├── deduplicator.py
│   ├── embedder.py
│   ├── explainer.py
│   ├── filtering.py
│   ├── normalizer.py
│   ├── pipeline.py
│   ├── prompts.py
│   ├── query_parser.py
│   └── ranker.py
│
├── notebooks/
│   └── exploration.ipynb
│
├── requirements.txt
├── .gitignore
├── README.md
└── main.py
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Conversational-Book-Recommendation-Assistant-using-RAG.git
cd Conversational-Book-Recommendation-Assistant-using-RAG
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama
This project uses a local LLM through Ollama. Install Ollama and pull the model configured in your project:
```bash
ollama run gemma3
```

---

## Running the Project

### Launch the Streamlit app
```bash
streamlit run app/app.py
```

### Run the backend pipeline directly (no UI)
```bash
python main.py
```

Useful for debugging or testing the backend workflow independently.

---

## Configuration

Before running, verify the following settings match your local environment. These are typically defined in `src/pipeline.py`, `src/api_clients.py`, `src/prompts.py`, and `src/ranker.py`:

- Ollama model name
- Number of recommendations returned
- Retrieval parameters for API search
- Ranking logic and weighting
- Retry and throttling settings for external API calls

---

## Key Takeaways

- Natural-language requests can be converted into retrieval-friendly atomic tags
- Tag-based retrieval significantly outperforms sending raw prompts to public book APIs
- Using multiple sources improves book coverage
- Cleaning and deduplicating results improves recommendation quality
- A lightweight RAG-style workflow produces more grounded recommendations than a purely generative approach
- Recommendation quality depends not just on the LLM, but on retrieval quality, metadata quality, and ranking design

---

## Limitations

- Recommendation quality depends on metadata available from public APIs (descriptions, categories, authors can be incomplete)
- Ranking is heuristic-based, not learned from real user feedback
- Public API results can occasionally be noisy or irrelevant
- API rate limits and inconsistent responses can affect reliability

---

## Future Improvements

- Support for negative preferences (e.g. *"no fantasy"*, *"no dark romance"*)
- Improved ranking using semantic similarity
- Feedback loop (*"show me more like this"*)
- Filters for genre, year, rating, language, or length
- Past search and recommendation history
- Online deployment for public use

---

## Author

**Sanjeevani Rajpurohit**  
Master's student in Data Science — interests in NLP, recommender systems, machine learning, and practical AI applications.