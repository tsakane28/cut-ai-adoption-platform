import os
import requests
import json
import streamlit as st

def get_api_key():
    """
    Get the OpenRouter API key from environment variables
    
    Returns:
        str: API key or None if not found
    """
    # Try to get from environment variables or use a demo key (for development only)
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # For demonstration purposes - in production, this should be removed
    if not api_key:
        st.warning("OpenRouter API key not found in environment variables. Using mock data for demonstration.")
        return None
    
    return api_key

def get_ai_insights(prompt):
    """
    Get AI-generated insights using OpenRouter API
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        str: Generated insights
    """
    api_key = get_api_key()
    
    # If no API key is available, return mock insights
    if not api_key:
        return generate_mock_insights()
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Request body
    data = {
        "model": "anthropic/claude-3-opus:beta",  # Can be adjusted based on needs
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        # Make the request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # Check for successful response
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            # Return the generated text
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"Error from OpenRouter API: {response.status_code} - {response.text}")
            return generate_mock_insights()
    
    except Exception as e:
        st.error(f"Exception when calling OpenRouter API: {str(e)}")
        return generate_mock_insights()

def generate_mock_insights():
    """
    Generate mock insights for demonstration purposes
    
    Returns:
        str: Mock insights text
    """
    return """Insights:
1. The majority of respondents (58%) are somewhat familiar with AI tools, but there's a significant portion (25%) who aren't familiar at all, indicating a need for basic AI literacy.
2. The most commonly used AI tools are Turnitin (48%), Grammarly (42%), and ChatGPT (37%), showing a focus on writing assistance and academic integrity.
3. Technical issues and lack of training are the top challenges faced by users, suggesting infrastructure and education gaps.
4. Faculty affiliation significantly correlates with AI adoption rates, with Engineering and Business faculties showing higher adoption than Health Sciences and Education.
5. There's a moderate positive correlation between AI familiarity and perception of learning improvement, indicating that understanding AI leads to better learning outcomes.

Recommendations:
1. Implement targeted AI literacy workshops, particularly for those faculties with lower adoption rates, focusing on basic understanding and practical applications.
2. Address technical infrastructure issues by establishing dedicated AI help desks and releasing step-by-step guides for the most common tools.
3. Develop faculty-specific use cases showcasing how AI tools can enhance teaching and learning in different disciplines to encourage adoption across all departments."""
