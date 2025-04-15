import pandas as pd
import numpy as np

def preprocess_data(data):
    """
    Preprocess the survey data for analysis and modeling.
    
    Args:
        data (pd.DataFrame): Raw survey data
    
    Returns:
        pd.DataFrame: Processed data ready for analysis
    """
    # Make a copy to avoid modifying original data
    df = data.copy()
    
    # Handle missing values
    df = df.fillna({
        "4. AI familiarity": "Not familiar at all",
        "5. Used AI tools": "None",
        "6. Tools used": "None",
        "7. Usage frequency": 1,
        "8. Challenges": "None",
        "10. Improves learning?": "No"
    })
    
    # Ensure used_ai_tools column exists and is populated from "5. Used AI tools"
    df["used_ai_tools"] = df["5. Used AI tools"]
    
    # Convert usage frequency to numeric
    df["7. Usage frequency"] = pd.to_numeric(df["7. Usage frequency"], errors="coerce").fillna(1)
    
    # Create tools count feature
    df["tools_count"] = df["6. Tools used"].apply(
        lambda x: 0 if x == "None" else len(str(x).split(", "))
    )
    
    # Create challenges count feature
    df["challenges_count"] = df["8. Challenges"].apply(
        lambda x: 0 if x == "None" else len(str(x).split(", "))
    )
    
    # Create binary target for model training
    df["adoption_positive"] = df["10. Improves learning?"].apply(
        lambda x: 1 if x == "Yes" else 0
    )
    
    return df

def get_survey_stats(data):
    """
    Calculate basic statistics from the survey data
    
    Args:
        data (pd.DataFrame): Processed survey data
    
    Returns:
        dict: Dictionary of basic statistics
    """
    stats = {
        "total_responses": len(data),
        "unique_tools": data["6. Tools used"].str.split(", ").explode().nunique(),
        "avg_frequency": data["7. Usage frequency"].mean(),
        "familiarity_levels": data["4. AI familiarity"].value_counts().to_dict(),
        "top_challenges": data["8. Challenges"].value_counts().nlargest(3).to_dict(),
        "positive_impact_pct": (data["10. Improves learning?"] == "Yes").mean() * 100
    }
    
    return stats

def extract_tools(tools_str):
    """
    Extract individual tools from comma-separated string
    
    Args:
        tools_str (str): Comma-separated string of tools
        
    Returns:
        list: List of individual tools
    """
    if pd.isna(tools_str) or tools_str == "None":
        return []
    
    # Split by comma and handle potential spaces
    tools = [tool.strip() for tool in tools_str.split(",")]
    return tools

def extract_challenges(challenges_str):
    """
    Extract individual challenges from comma-separated string
    
    Args:
        challenges_str (str): Comma-separated string of challenges
        
    Returns:
        list: List of individual challenges
    """
    if pd.isna(challenges_str) or challenges_str == "None":
        return []
    
    # Split by comma and handle potential spaces
    challenges = [challenge.strip() for challenge in challenges_str.split(",")]
    return challenges
