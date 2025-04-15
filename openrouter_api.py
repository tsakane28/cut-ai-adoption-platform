import os
import requests
import json
import streamlit as st
from loggers import get_logger

# Set up logger
logger = get_logger("openrouter_api")

# Default OpenRouter configuration
DEFAULT_API_KEY = "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"
DEFAULT_MODEL_ID = "deepseek/deepseek-r1-distill-qwen-32b:free"
DEFAULT_MODEL_NAME = "DeepSeek R1 Distill Qwen 32B"

def get_api_key():
    """
    Get the OpenRouter API key from environment variables
    
    Returns:
        str: API key or None if not found
    """
    # Try to get from environment variables
    api_key = os.getenv("OPENROUTER_API_KEY", DEFAULT_API_KEY)
    
    if not api_key:
        logger.warning("OpenRouter API key not found in environment variables")
        st.warning("OpenRouter API key not found in environment variables. Using mock data for demonstration.")
        return None
    
    logger.info("Successfully loaded OpenRouter API key")
    return api_key

def get_model_id():
    """
    Get the OpenRouter model ID from environment variables
    
    Returns:
        str: Model ID or default model if not found
    """
    model_id = os.getenv("OPENROUTER_MODEL_ID", DEFAULT_MODEL_ID)
    logger.info(f"Using OpenRouter model ID: {model_id}")
    return model_id

def get_model_name():
    """
    Get the OpenRouter model name from environment variables
    
    Returns:
        str: Model name or default model name if not found
    """
    return os.getenv("OPENROUTER_MODEL_NAME", DEFAULT_MODEL_NAME)

def get_ai_insights(prompt):
    """
    Get AI-generated insights using OpenRouter API
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        str: Generated insights
    """
    api_key = get_api_key()
    model_id = get_model_id()
    
    # If no API key is available, return mock insights
    if not api_key:
        logger.warning("No API key available, using mock insights")
        return generate_mock_insights()
    
    logger.info(f"Using OpenRouter API with model: {model_id}")
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ccut-ai-adoption-platform.replit.app",
        "X-Title": "CUT AI Adoption Analytics Platform",
        "OpenAI-Beta": "assistants=v1"
    }
    
    # Request body
    data = {
        "model": model_id,
        "route": "fallback",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI analytics expert specializing in educational technology adoption and data analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "headers": {
            "HTTP-Referer": "https://ccut-ai-adoption-platform.replit.app",
            "X-Title": "CUT AI Adoption Analytics Platform"
        }
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
