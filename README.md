# Conversational Book Recommendation Assistant using RAG

A conversational book recommendation system that converts a user's natural-language reading preferences into relevant book suggestions using a Retrieval-Augmented Generation (RAG) pipeline.

Instead of relying only on a language model to generate recommendations directly, this project uses a structured workflow:
- interpret the user's request
- generate focused retrieval tags/keywords
- fetch books from external public sources
- clean and enrich the retrieved metadata
- rank the books for more relevant final recommendations

This makes the system more practical and reliable for real book recommendation use cases.

---

## Overview

Users often describe the kind of books they want in a natural, conversational way rather than with clean search keywords.

Examples:
- “I want books that help me become more disciplined”
- “Recommend fantasy books with political intrigue and morally grey characters”
- “I want an emotional romance but not something toxic”
- “Suggest comforting books for a reading slump”

Public book APIs do not always handle these long, messy queries well. This project addresses that problem by first converting the user's prompt into better retrieval tags, then using those tags to fetch and rank candidate books.

---

## Motivation

Traditional search-based recommendation often performs poorly when users express preferences conversationally.

A long natural-language request can be:
- too broad
- too specific
- too noisy
- poorly suited for direct API retrieval

This project was built to solve that by creating a lightweight end-to-end recommendation assistant that combines:
- LLM-based query understanding
- external retrieval from book APIs
- preprocessing and deduplication
- ranking logic
- an interactive Streamlit interface

It is designed as a portfolio project that demonstrates practical NLP, retrieval, data processing, and application development skills.

---

## Features

- Conversational input for book preferences
- LLM-based tag and keyword generation
- Retrieval from public book APIs
- Data cleaning and normalization
- Deduplication across multiple sources
- Metadata enrichment where available
- Relevance-based ranking
- Streamlit user interface
- Modular and extensible project structure

---

## How the System Works

### 1. User enters a request
The user describes the type of book they are looking for in natural language.

Example:
> I want a motivating self-help book that helps me become more disciplined and improve my habits.

### 2. Tags are generated from the request
Instead of using the full query directly for retrieval, the system extracts focused keywords and tags.

Example generated tags:
- discipline
- habits
- self-help
- productivity
- motivation
- personal growth

### 3. Candidate books are retrieved
These tags are used to search external sources such as:
- Google Books
- Open Library

### 4. Results are cleaned and standardized
Returned book data is normalized across sources. This includes fields such as:
- title
- authors
- description
- categories
- ratings
- identifiers

### 5. Duplicate books are removed
Books retrieved from different APIs may overlap, so duplicates are identified and removed.

### 6. Metadata is enriched
Where possible, missing fields are supplemented using information from merged API results.

### 7. Books are ranked
Candidate books are scored and ranked based on relevance to the generated tags and the quality of their metadata.

### 8. Final recommendations are displayed
The user receives a curated list of book recommendations through the Streamlit app.

---

## Tech Stack

- **Python**
- **Streamlit**
- **Ollama / local LLM**
- **Google Books API**
- **Open Library API**
- **Pandas**
- **Requests**

---

## Project Structure
```bash

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

## Installation

### 1. Clone the repository
Clone the project from GitHub and move into the project folder.
```bash
git clone https://github.com/your-username/Conversational-Book-Recommendation-Assistant-using-RAG.git
cd Conversational-Book-Recommendation-Assistant-using-RAG
