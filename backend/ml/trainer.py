import asyncio
import os
import sys
import joblib
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from motor.motor_asyncio import AsyncIOMotorClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from ml.categorizer import keyword_categorize

MONGODB_URL = os.getenv("MONGODB_URL")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "categorizer.pkl")


async def fetch_training_data():
    """
    Fetch all categorized expenses from MongoDB.
    Only use expenses that are NOT 'Uncategorized' or 'Other'.
    """
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]

    cursor = db["expenses"].find(
        {"category": {"$nin": ["Uncategorized", "Other"]}},
        {"merchant": 1, "category": 1}
    )

    data = await cursor.to_list(length=10000)
    client.close()
    return data


def evaluate_keyword_baseline(X_test, y_test):
    """
    Evaluate keyword baseline on test set.
    Returns accuracy score.
    """
    correct = 0
    for merchant, true_label in zip(X_test, y_test):
        predicted, _ = keyword_categorize(merchant)
        if predicted == true_label:
            correct += 1
    baseline_accuracy = correct / len(y_test)
    return baseline_accuracy


async def train():
    print("Fetching training data from MongoDB...")
    data = await fetch_training_data()
    print(f"Found {len(data)} labeled transactions")

    if len(data) < 50:
        print("❌ Not enough data to train. Need at least 50 labeled transactions.")
        return

    X = [doc["merchant"] for doc in data]
    y = [doc["category"] for doc in data]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    print("\nEvaluating keyword baseline...")
    baseline_accuracy = evaluate_keyword_baseline(X_test, y_test)
    print(f"Keyword Baseline Accuracy: {baseline_accuracy:.1%}")

    print("\nTraining TF-IDF + Logistic Regression model...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=5000,
            lowercase=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
        )),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    ml_accuracy = accuracy_score(y_test, y_pred)

    print(f"ML Model Accuracy:         {ml_accuracy:.1%}")

    print("\n── Accuracy Comparison ────────────────────")
    print(f"  Keyword Baseline:  {baseline_accuracy:.1%}")
    print(f"  ML Model:          {ml_accuracy:.1%}")
    print(f"  Improvement:       +{(ml_accuracy - baseline_accuracy):.1%}")
    print("─────────────────────────────────────────")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    model_data = {
        "pipeline": pipeline,
        "baseline_accuracy": baseline_accuracy,
        "ml_accuracy": ml_accuracy,
        "improvement": ml_accuracy - baseline_accuracy,
        "trained_at": datetime.now().isoformat(),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "categories": list(set(y)),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }

    joblib.dump(model_data, MODEL_PATH)
    print(f"\n✅ Model saved to {MODEL_PATH}")

    return model_data


if __name__ == "__main__":
    asyncio.run(train())