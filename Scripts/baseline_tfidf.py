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






