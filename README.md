# CUT AI Adoption Analytics Platform

A Streamlit-based AI predictive analytics platform for analyzing CUT survey data with OpenRouter AI integration for insights and suggestions, PostgreSQL database integration, and Docker containerization.

## Features

- Data visualization dashboard showing key metrics from the training CSV
- AI predictive model integration using the provided training data
- Generate insights and suggestions using OpenRouter's generative AI capabilities
- Interactive data exploration and filtering options
- PostgreSQL database for persistent storage of survey data, predictions, and insights
- Docker containerization for easy deployment and scalability

## Technologies Used

- Python 3.11
- Streamlit
- Pandas & NumPy
- Plotly for data visualization
- Scikit-learn for machine learning models
- OpenRouter API for AI-generated insights
- SQLAlchemy ORM for database operations
- PostgreSQL database for data persistence
- Docker & Docker Compose for containerization

## Installation

### Standard Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - OPENROUTER_API_KEY: Your OpenRouter API key
   - DATABASE_URL: PostgreSQL database connection URL

### Docker Installation (Recommended)

1. Clone this repository
2. Make sure Docker and Docker Compose are installed
3. Run the Docker setup utility:
   ```
   python docker_setup.py
   ```
   or manually build and start containers:
   ```
   docker-compose build
   docker-compose up -d
   ```
4. Access the application at http://localhost:5000

## Usage

1. Run the application:
   - Standard: `streamlit run app.py`
   - Docker: Access http://localhost:5000 after starting containers
2. Upload the survey data CSV file
3. Explore visualizations, predictions, and AI-generated insights
4. All data will be saved to the PostgreSQL database for persistence

## Database Schema

The application uses a PostgreSQL database with the following tables:

- `surveys`: Stores survey responses data
- `predictions`: Stores AI adoption predictions
- `insights`: Stores AI-generated insights and recommendations

## Project Structure

- `app.py`: Main Streamlit application
- `utils.py`: Data preprocessing and utility functions
- `model.py`: Machine learning model for AI adoption prediction
- `data_viz.py`: Data visualization functions
- `openrouter_api.py`: OpenRouter API integration
- `database.py`: Database models and operations using SQLAlchemy
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Multi-container Docker configuration
- `docker_setup.py`: Utility script for Docker setup and management

## Docker Management

You can manage Docker containers using the provided utility script:

```
python docker_setup.py
```

This will display a menu with options to:

1. Build and start containers
2. Stop containers
3. Restart containers
4. Show container logs
5. Initialize database

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DATABASE_URL`: PostgreSQL database connection URL
- `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGHOST`, `PGPORT`: PostgreSQL connection details