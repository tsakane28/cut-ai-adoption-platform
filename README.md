# CUT AI Adoption Analytics Platform

A Streamlit-based AI predictive analytics platform for analyzing CUT survey data with OpenRouter AI integration for insights and suggestions.

## Features

- Data visualization dashboard showing key metrics from the training CSV
- AI predictive model integration using the provided training data
- Generate insights and suggestions using OpenRouter's generative AI capabilities
- Interactive data exploration and filtering options

## Technologies Used

- Python 3.11
- Streamlit
- Pandas & NumPy
- Plotly for data visualization
- Scikit-learn for machine learning models
- OpenRouter API for AI-generated insights

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - OPENROUTER_API_KEY: Your OpenRouter API key

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```
2. Upload the survey data CSV file
3. Explore visualizations, predictions, and AI-generated insights

## Project Structure

- `app.py`: Main Streamlit application
- `utils.py`: Data preprocessing and utility functions
- `model.py`: Machine learning model for AI adoption prediction
- `data_viz.py`: Data visualization functions
- `openrouter_api.py`: OpenRouter API integration