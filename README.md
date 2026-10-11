# Helpdesk FAQ Chatbot

A lightweight FAQ chatbot with a responsive web chat interface. It preprocesses questions with NLTK, matches them to an editable FAQ knowledge base using TF-IDF and cosine similarity, and returns the closest answer with a match score.

## Features

- NLTK tokenization and text normalization (no downloaded NLTK corpora required).
- TF-IDF vectors with unigrams and bigrams; cosine similarity ranks candidate FAQs.
- Editable `faq_data.json` data with questions, answers, categories, and optional keywords.
- Confidence threshold and a helpful fallback response for unmatched questions.
- Responsive chat UI, clickable example questions, keyboard submit, and suggestions.
- Flask JSON endpoint at `POST /api/chat`.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the app with `python app.py`.
4. Open http://127.0.0.1:5000 in your browser.

The first run does not download any language data. The default FAQ sample is about a general online shop; replace or extend `faq_data.json` to customize the chatbot for your product.

## Customize matching

Each FAQ is a JSON object with required `question` and `answer` strings, plus optional `category` and `keywords` fields. Add likely alternate phrasings to `keywords` to improve recall. The matching cutoff defaults to `0.16`; set `FAQ_MATCH_THRESHOLD` to tune strictness. Set `FAQ_DATA_PATH` to load a different JSON file and `PORT` to change the local server port.

The `POST /api/chat` request body is `{ "question": "Where is my order?" }`. A matching response includes `answer`, `matchedQuestion`, `category`, and `confidence`. Unmatched requests include a fallback answer and suggested questions.

## Tests

Run the automated tests with `python -m unittest discover -s tests`.
