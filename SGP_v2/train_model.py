import pandas as pd
import numpy as np # Import numpy for np.save
import joblib
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.metrics import jaccard_score, f1_score, precision_score, recall_score
from sklearn.multioutput import MultiOutputClassifier
from sentence_transformers import SentenceTransformer # NEW: Import SentenceTransformer
import os # Import os for directory creation

# --- Custom Transformers ---
class TextListTransformer(BaseEstimator, TransformerMixin):
    """
    Transforms a column of comma-separated strings (or lists) into a single
    space-separated string, suitable for TF-IDF vectorization.
    Handles potential NaN values by treating them as empty strings.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Fill NaN values with empty string before joining, then replace ", " with " "
        return X[self.column].fillna('').apply(lambda x: str(x).replace(", ", " ")).values.astype(str)

class NumericColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Selects a specific numerical column from the DataFrame and returns it
    as a 2D array, which is required by scikit-learn transformers like StandardScaler.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.column]]

class CategoricalColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Selects a specific categorical column from the DataFrame and returns it
    as a 2D array, suitable for OneHotEncoder.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.column]]

# --- Load Data ---
csv_file_path = "SGP_v2\data\synthetic_career_data.csv"
try:
    df = pd.read_csv(csv_file_path)
    print(f"Dataset loaded from {csv_file_path}")
except FileNotFoundError:
    print(f"Error: {csv_file_path} not found. Please run the `synthetic_dataset_generator.py` script first.")
    exit()

# Convert comma-separated strings back to lists for MultiLabelBinarizer for the target variable
# And for other text columns as well, because the custom transformer expects list-like input
for col in ["Interest_Areas", "Soft_Skills", "Programming_Languages", "Tools_and_Techstack",
            "Current_Certifications", "Extracurricular_Interests", "Favourite_Subjects",
            "Problem_Solving_Style", "Recommended_Career"]:
    # Handle NaN values explicitly, convert to list of strings
    df[col] = df[col].apply(lambda x: [item.strip() for item in str(x).split(', ')] if pd.notna(x) and x != '' else [])


# --- Prepare Target Variable (MultiLabelBinarizer) ---
mlb = MultiLabelBinarizer()
# Fit and transform the 'Recommended_Career' column to get the binary target matrix
y = mlb.fit_transform(df['Recommended_Career'])
print(f"Total unique career options identified: {len(mlb.classes_)}")
print(f"Career labels: {mlb.classes_}")

# --- Semantic Embeddings Generation ---
print("\nLoading Sentence-BERT model for semantic embeddings...")
# Using a small, fast model suitable for quick inference. 'all-MiniLM-L6-v2' is a good choice.
# This model will be downloaded the first time it's run.
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Sentence-BERT model loaded.")

# Combine relevant text columns into a single string for embedding
# This creates a comprehensive textual representation of each student's profile
df['combined_text_features'] = df.apply(
    lambda row: ' '.join(
        row['Interest_Areas'] +
        row['Soft_Skills'] +
        row['Programming_Languages'] +
        row['Tools_and_Techstack'] +
        row['Current_Certifications'] +
        row['Extracurricular_Interests'] +
        row['Favourite_Subjects'] +
        row['Problem_Solving_Style']
    ), axis=1
)

print("Generating semantic embeddings for the dataset (this may take a moment)...")
# Generate embeddings for all combined text features
student_embeddings = sentence_model.encode(df['combined_text_features'].tolist(), show_progress_bar=True)
print(f"Generated embeddings shape: {student_embeddings.shape}")

# Ensure the 'models' directory exists
os.makedirs('models', exist_ok=True)

# Save the embeddings to a .npy file
np.save('SGP_v2\models\student_embeddings.npy', student_embeddings)
print("Student embeddings saved to 'models/student_embeddings.npy'.")

# --- Feature Engineering and Preprocessing Pipeline ---
numeric_features = ["CGPA", "Current_Projects_Count", "Expected_Salary_Range"]
categorical_features = ["Preferred_Work_Style", "Wants_to_Go_for_Masters", "Interested_in_Research",
                        "Internship_Experience", "Team_vs_Solo_Preference"]
text_features = ["Interest_Areas", "Soft_Skills", "Programming_Languages", "Tools_and_Techstack",
                 "Current_Certifications", "Extracurricular_Interests", "Favourite_Subjects",
                 "Problem_Solving_Style"]

features_pipeline = []
for col in numeric_features:
    features_pipeline.append((f"numeric_{col}", Pipeline([
        (f"selector_{col}", NumericColumnTransformer(col)),
        (f"scaler_{col}", StandardScaler())
    ])))
for col in categorical_features:
    features_pipeline.append((f"categorical_{col}", Pipeline([
        (f"selector_{col}", CategoricalColumnTransformer(col)),
        (f"onehot_{col}", OneHotEncoder(handle_unknown='ignore'))
    ])))
for col in text_features:
    features_pipeline.append((f"text_{col}", Pipeline([
        (f"selector_{col}", TextListTransformer(col)),
        (f"tfidf_{col}", TfidfVectorizer(max_features=100, stop_words=None))
    ])))

preprocessor = FeatureUnion(transformer_list=features_pipeline)

# --- Model Training ---
classifier = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1))
model_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', classifier)
])

# Exclude 'combined_text_features' (used only for semantic search) from the ML classification model's input
X = df.drop(columns=['Recommended_Career', 'combined_text_features'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\nTraining ML classification model...")
model_pipeline.fit(X_train, y_train)
print("ML classification model training complete.")

# --- Evaluation ---
y_pred = model_pipeline.predict(X_test)

print("\nML Model Evaluation (on Test Set):")
print(f"Jaccard Score (Avg): {jaccard_score(y_test, y_pred, average='samples'):.4f}")
print(f"F1 Score (Micro): {f1_score(y_test, y_pred, average='micro'):.4f}")
print(f"F1 Score (Macro): {f1_score(y_test, y_pred, average='macro'):.4f}")
print(f"Precision Score (Micro): {precision_score(y_test, y_pred, average='micro'):.4f}")
print(f"Recall Score (Micro): {recall_score(y_test, y_pred, average='micro'):.4f}")

# --- Save Model and Preprocessors ---
joblib.dump(mlb, 'SGP_v2\models\mlb.pkl')
joblib.dump(model_pipeline, 'SGP_v2\models\model_pipeline.pkl')
print("\nModel pipeline and MultiLabelBinarizer saved to 'SGP_v2\models\' directory.")