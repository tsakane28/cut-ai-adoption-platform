#!/bin/bash
set -e

# Initialize the database if it doesn't exist
python -c "from database import init_db; init_db()"

# Start the Streamlit application
streamlit run app.py --server.port=5000 --server.address=0.0.0.0