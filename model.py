
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

def prepare_features(data):
    """
    Prepare features for the prediction model
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        tuple: X (features) and y (target)
    """
    # Select features with more predictive power
    features = [
        "2. Level of study",
        "3. Faculty",
        "4. AI familiarity",
        "7. Usage frequency",
        "tools_count",
        "challenges_count",
        "used_ai_tools",
        "6. Tools used"
    ]
    
    # Select target
    target = "adoption_positive"
    
    # Create feature matrix and target vector
    X = data[features]
    y = data[target]
    
    return X, y

def train_model(data):
    """
    Train a prediction model for AI adoption
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        tuple: Trained model and accuracy score
    """
    # Prepare features and target
    X, y = prepare_features(data)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Define categorical and numerical features
    categorical_features = ["2. Level of study", "3. Faculty", "4. AI familiarity", "used_ai_tools", "6. Tools used"]
    numerical_features = ["7. Usage frequency", "tools_count", "challenges_count"]
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
            ]), categorical_features),
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numerical_features)
        ]
    )
    
    # Define model parameters for grid search
    rf_params = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [10, 20, None],
        'classifier__min_samples_split': [2, 5],
        'classifier__min_samples_leaf': [1, 2],
        'classifier__class_weight': ['balanced', None]
    }
    
    # Create pipeline
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('feature_selector', SelectFromModel(RandomForestClassifier(n_estimators=100, random_state=42))),
        ('classifier', RandomForestClassifier(random_state=42))
    ])
    
    # Perform grid search
    grid_search = GridSearchCV(
        model,
        rf_params,
        cv=5,
        scoring='accuracy',
        n_jobs=-1
    )
    
    # Train model
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_model = grid_search.best_estimator_
    
    # Evaluate model
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Perform cross-validation
    cv_scores = cross_val_score(best_model, X, y, cv=5)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Average CV accuracy: {cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
    
    return best_model, accuracy

def predict_adoption(model, data):
    """
    Make predictions using the trained model
    
    Args:
        model: Trained model
        data (pd.DataFrame): Processed survey data
        
    Returns:
        array: Prediction probabilities
    """
    # Prepare features
    X, _ = prepare_features(data)
    
    # Make predictions (probability of positive class)
    predictions = model.predict_proba(X)[:, 1]
    
    return predictions
