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

df = df.dropna(subset=["Passage", "risk_category"])
print(df.head())



