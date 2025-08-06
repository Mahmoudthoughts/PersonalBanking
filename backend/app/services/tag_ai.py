"""AI-powered tag suggestions using scikit-learn."""

from __future__ import annotations

import logging
import threading
import time
from typing import List, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier

from ..models import Transaction, Tag


class TagAI:
    """Train a model to predict tags from transaction descriptions."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.classifier = MultiOutputClassifier(LogisticRegression(max_iter=1000))
        self.tag_ids: List[int] = []
        self.trained = False

    def train(self) -> None:
        """Gather training data from existing transactions and fit the model."""
        transactions = Transaction.query.join(Transaction.tags).all()
        texts: List[str] = []
        labels: List[List[int]] = []

        tags = Tag.query.all()
        self.tag_ids = [t.id for t in tags]
        tag_index: Dict[int, int] = {tid: i for i, tid in enumerate(self.tag_ids)}

        for tx in transactions:
            if not tx.description:
                continue
            texts.append(tx.description)
            row = [0] * len(self.tag_ids)
            for tag in tx.tags:
                idx = tag_index.get(tag.id)
                if idx is not None:
                    row[idx] = 1
            labels.append(row)

        if not texts:
            logging.warning("TagAI: no training data available")
            return

        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        self.classifier.fit(X, y)
        self.trained = True
        logging.info("TagAI: trained on %d transactions", len(texts))

    def suggest(self, description: str, top_n: int = 5) -> List[Dict[str, float]]:
        """Return top-N tag suggestions for the given description."""
        if not self.trained or not description:
            return []
        X = self.vectorizer.transform([description])
        probas = self.classifier.predict_proba(X)
        scores = [p[1] for p in probas]
        ranked = np.argsort(scores)[::-1]
        suggestions = []
        for idx in ranked[:top_n]:
            score = float(scores[idx])
            if score <= 0:
                continue
            tag = Tag.query.get(self.tag_ids[idx])
            if tag:
                suggestions.append({"id": tag.id, "name": tag.name, "score": score})
        return suggestions


tag_ai = TagAI()


def schedule_training(app, interval: int = 3600) -> None:
    """Start a background thread that periodically retrains the model."""

    def run():
        while True:
            with app.app_context():
                try:
                    tag_ai.train()
                except Exception as exc:  # pragma: no cover - background logging
                    logging.exception("TagAI training failed: %s", exc)
            time.sleep(interval)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
