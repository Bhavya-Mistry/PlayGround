import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score

# Load your data
df = pd.read_csv(r'career-navigator\v2\data\19k.csv')  # Uncomment and load your dataset

# Preprocessing: Split the data into X (features) and y (target)
X = df.drop(columns=['Recommended_Career'])
y = df['Recommended_Career']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing for numeric and categorical features
numeric_features = ['CGPA', 'Current_Projects_Count', 'Internship_Experience']
categorical_features = [col for col in X.columns if col not in numeric_features]

# Preprocessing for numeric features: scale them
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),  # Impute missing values with the mean
    ('scaler', StandardScaler())  # Standardize the data
])

# Preprocessing for categorical features: one-hot encode them
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),  # Impute missing values with the most frequent value
    ('onehot', OneHotEncoder(handle_unknown='ignore'))  # One-Hot Encoding
])

# Bundle preprocessing for numeric and categorical data
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Random Forest Classifier pipeline
rf_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),  # Preprocessing
    ('classifier', RandomForestClassifier(random_state=42, n_jobs=-1))  # Random Forest Classifier
])

# Hyperparameter tuning with GridSearchCV
param_grid = {
    'classifier__n_estimators': [100, 200, 300],  # Number of trees
    'classifier__max_depth': [None, 10, 20, 30],  # Depth of each tree
    'classifier__min_samples_split': [2, 5, 10],  # Minimum samples required to split a node
    'classifier__min_samples_leaf': [1, 2, 4],  # Minimum samples required at leaf nodes
    'classifier__max_features': ['sqrt', 'log2', None],  # Number of features to consider for splitting
}

# Set up GridSearchCV to search over the hyperparameters
grid_search = GridSearchCV(rf_pipeline, param_grid, cv=StratifiedKFold(5), n_jobs=-1, verbose=1, scoring='accuracy')

# Fit the model with grid search
grid_search.fit(X_train, y_train)

# Get the best parameters from the grid search
best_params = grid_search.best_params_
print(f"Best parameters found: {best_params}")

# Train the model with the best parameters found
best_rf_pipeline = grid_search.best_estimator_

# Evaluate the model on the training and test data
train_preds = best_rf_pipeline.predict(X_train)
test_preds = best_rf_pipeline.predict(X_test)

train_accuracy = accuracy_score(y_train, train_preds)
train_f1 = f1_score(y_train, train_preds, average='weighted')

test_accuracy = accuracy_score(y_test, test_preds)
test_f1 = f1_score(y_test, test_preds, average='weighted')

# Output the results for training and test data
print(f"Training Accuracy: {train_accuracy:.4f}")
print(f"Training F1 Score: {train_f1:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")
print(f"Test F1 Score: {test_f1:.4f}")

# Cross-validation for better evaluation
cross_val_accuracy = cross_val_score(best_rf_pipeline, X, y, cv=StratifiedKFold(5), scoring='accuracy')
cross_val_f1 = cross_val_score(best_rf_pipeline, X, y, cv=StratifiedKFold(5), scoring='f1_weighted')

print(f"Cross-validation Accuracy: {cross_val_accuracy.mean():.4f}")
print(f"Cross-validation F1 Score: {cross_val_f1.mean():.4f}")

# Evaluate overfitting/underfitting
if train_accuracy > test_accuracy:
    print("The model may be overfitting.")
elif train_accuracy < test_accuracy:
    print("The model may be underfitting.")
else:
    print("The model's performance is balanced.")
