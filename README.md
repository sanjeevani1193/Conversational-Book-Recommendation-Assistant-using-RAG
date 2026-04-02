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

---

## Installation

### 1. Clone the repository
Clone the project from GitHub and move into the project folder.

```bash
git clone https://github.com/your-username/Conversational-Book-Recommendation-Assistant-using-RAG.git
cd Conversational-Book-Recommendation-Assistant-using-RAG

### 2. Create and activate a virtual environment
Create a virtual environment to keep project dependencies isolated.

```bash
python -m venv venv
source venv/bin/activate

For Windows:
```bash
venv\Scripts\activate

### 3. Install dependencies
Install all required Python libraries from the requirements.txt file.

```bash
pip install -r requirements.txt

### 4. Install and start Ollama
This project uses a local LLM through Ollama for query understanding and tag generation, so Ollama must be installed and running before starting the app.

Example: 

```bash
ollama run llama3

Use the same model name that is configured in your project files.

---

## How to Run the Project

### Run the Streamlit app
Use this command to launch the user interface:

```bash
streamlit run app/app.py

This opens the conversational recommendation app in the browser, where users can enter natural-language reading preferences and receive ranked book suggestions.

### Run the main script
If you want to test the recommendation pipeline directly without the UI, run:

```bash
python main.py

This is useful for debugging or testing the backend workflow separately from Streamlit.

---

## Configuration
A few project settings may need to be adjusted depending on your local setup and chosen model.
- Typical configuration areas include:
- the Ollama model name
- the number of recommendations returned
- retrieval parameters used for API search
- ranking logic or weighting rules
- retry/throttling settings for external API calls

These values are usually defined in files such as:
- src/pipeline.py
- src/api_clients.py
- src/prompts.py
- src/ranker.py
Before running the project, make sure these settings match your local environment and the model you want to use.

## Results and Takeaways
This project showed that conversational book recommendation can be improved by breaking the problem into multiple structured steps instead of relying only on direct language-model output.
Some main takeaways from the project are:
- natural-language user requests can be converted into retrieval-friendly tags
- tag-based retrieval performs better than sending long raw prompts directly to public book APIs
- using multiple sources improves book coverage
- cleaning and deduplicating results improves recommendation quality
- a lightweight RAG-style workflow can produce more grounded and useful recommendations than a purely generative approach
- A major insight from this project is that recommendation quality depends not only on the language model, but also on retrieval quality, metadata quality, and ranking design.

---

## Limitations
Although the system works well as a portfolio project and proof of concept, it still has a few limitations.
- recommendation quality depends on the metadata available from public APIs
- some books have incomplete or inconsistent fields such as descriptions, categories, or author names
- public API results can sometimes be noisy or weak
- ranking is heuristic-based and not learned from real user feedback
- final output depends partly on how well the LLM generates useful retrieval tags
- API rate limits and inconsistent responses can affect reliability
- These limitations show that recommendation systems are influenced by both model quality and data quality.

---

## Future Improvements
There are several possible ways to improve this project in the future.
- add support for negative preferences such as “no fantasy” or “no dark romance”
- improve ranking using embeddings or semantic similarity
- add a feedback loop such as “show me more like this”
- support filters for genre, year, rating, language, or length
- store past searches and recommendations
- evaluate recommendation quality through user testing
- deploy the application online for public use
- These improvements would make the system more personalized, scalable, and closer to production-style recommender application.

--- 

## Replication steps
To replicate the full project workflow from scratch:
- Clone the repository
- Create and activate a virtual environment
- Install dependencies from requirements.txt
- Make sure Ollama is installed and running locally
- Launch the Streamlit app or run main.py
- Enter a conversational book request
- Review the generated tags, retrieved books, and final ranked recommendations
Following these steps reproduces the end-to-end pipeline used in this project.

---

## Reproducibility
This project is reproducible as long as the required packages are installed and the local LLM is available through Ollama.

To reproduce the behavior of the system:
- install all required dependencies
- ensure Ollama is running with the correct model
- run the application
- test it using natural-language reading queries

Because the project depends on live public APIs such as Google Books and Open Library, exact recommendation outputs may vary over time depending on API responses, available metadata, and source coverage. However, the overall workflow and system logic remain reproducible.

---

#Author
Sanjeevani Rajpurohit
Master’s student in Data Science with interests in NLP, recommender systems, machine learning, and practical AI applications.