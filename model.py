import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def prepare_features(data):
    """
    Prepare features for the prediction model
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        tuple: X (features) and y (target)
    """
    # Select features
    features = [
        "2. Level of study", 
        "3. Faculty", 
        "4. AI familiarity", 
        "7. Usage frequency", 
        "tools_count", 
        "challenges_count"
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
        X, y, test_size=0.2, random_state=42
    )
    
    # Define categorical and numerical features
    categorical_features = ["2. Level of study", "3. Faculty", "4. AI familiarity"]
    numerical_features = ["7. Usage frequency", "tools_count", "challenges_count"]
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ]), categorical_features),
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median'))
            ]), numerical_features)
        ]
    )
    
    # Create pipeline
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate model
    accuracy = model.score(X_test, y_test)
    
    return model, accuracy

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
