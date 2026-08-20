import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# loading dataset
df = pd.read_csv("Z:/Devin/Research/annotation_dataset_completed.csv")

df = df.dropna(subset=["Passage", "risk_category"]) # here we simply drop all empty values


#       Features and labels
# let the passsage column be x and the risk_category column be y
X = df["Passage"]
y = df["risk_category"]


#       Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# now we get a sample to train and test on
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")


#       TF-IDF and Logistic regression

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase = True,
            ngram_range = (1, 2),
            min_df = 1,
            max_df = 0.95
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter = 10000,
            class_weight = "balanced"
        )
    )
])


# -----------------------------
# 5. Train
# -----------------------------

model.fit(X_train, y_train)

# -----------------------------
# 6. Predict
# -----------------------------

y_pred = model.predict(X_test)

# -----------------------------
# 7. Evaluate
# -----------------------------

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("TF-IDF + Logistic Regression")
print("==============================")

print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# -----------------------------
# 8. Confusion Matrix
# -----------------------------

cm = confusion_matrix(y_test, y_pred)

print("\nConfusion Matrix:")
print(cm)






