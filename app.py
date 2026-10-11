from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request
from nltk.tokenize import wordpunct_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
FAQ_PATH = Path(os.environ.get("FAQ_DATA_PATH", BASE_DIR / "faq_data.json"))
MATCH_THRESHOLD = float(os.environ.get("FAQ_MATCH_THRESHOLD", "0.16"))


def clean_tokens(text: str) -> list[str]:
    """Normalize a question into meaningful word tokens using NLTK."""
    tokens = wordpunct_tokenize(text.lower())
    return [token for token in tokens if re.search(r"[a-z0-9]", token)]


def load_faqs(path: Path = FAQ_PATH) -> list[dict[str, Any]]:
    """Load and validate FAQ records from the editable JSON knowledge base."""
    with path.open(encoding="utf-8") as faq_file:
        faqs = json.load(faq_file)

    if not isinstance(faqs, list) or not faqs:
        raise ValueError("FAQ data must be a non-empty JSON array.")

    required = {"question", "answer"}
    for index, faq in enumerate(faqs):
        if not isinstance(faq, dict) or not required.issubset(faq):
            raise ValueError(f"FAQ item {index + 1} must include a question and answer.")
        if not isinstance(faq["question"], str) or not isinstance(faq["answer"], str):
            raise ValueError(f"FAQ item {index + 1} question and answer must be text.")
    return faqs


faqs = load_faqs()
vectorizer = TfidfVectorizer(
    tokenizer=clean_tokens,
    token_pattern=None,
    lowercase=False,
    ngram_range=(1, 2),
    stop_words="english",
    sublinear_tf=True,
)
faq_documents = [
    " ".join(
        [faq["question"], " ".join(faq.get("keywords", []))]
    )
    for faq in faqs
]
faq_matrix = vectorizer.fit_transform(faq_documents)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def find_best_faq(question: str) -> dict[str, Any]:
    """Return the closest FAQ answer, or a helpful fallback if confidence is low."""
    cleaned_question = question.strip()
    if not cleaned_question:
        return {
            "matched": False,
            "answer": "Type a question and I’ll look through the FAQs for you.",
            "confidence": 0.0,
            "suggestions": [],
        }

    question_vector = vectorizer.transform([cleaned_question])
    scores = cosine_similarity(question_vector, faq_matrix).ravel()
    best_index = int(scores.argmax())
    best_score = float(scores[best_index])

    if best_score < MATCH_THRESHOLD:
        return {
            "matched": False,
            "answer": "I couldn’t find a close match in these FAQs. Try asking about shipping, returns, payments, or your order—or contact our support team for help.",
            "confidence": round(best_score, 3),
            "suggestions": [faq["question"] for faq in faqs[:3]],
        }

    faq = faqs[best_index]
    return {
        "matched": True,
        "answer": faq["answer"],
        "matchedQuestion": faq["question"],
        "category": faq.get("category", "General"),
        "confidence": round(best_score, 3),
        "suggestions": [],
    }


@app.get("/")
def home():
    return render_template("index.html", faqs=faqs)


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    if not isinstance(question, str):
        return jsonify({"error": "Question must be text."}), 400
    if len(question) > 500:
        return jsonify({"error": "Please keep questions under 500 characters."}), 400
    return jsonify(find_best_faq(question))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
