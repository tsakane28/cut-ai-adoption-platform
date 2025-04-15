#!/usr/bin/env python3
"""
Initialize the database for the CUT AI Adoption Analytics Platform.
"""

import os
import pandas as pd
from database import init_db, load_survey_data_to_db
from utils import preprocess_data
from loggers import get_logger

# Set up logger
logger = get_logger("init_database")

def main():
    """Initialize database and load sample data if available."""
    logger.info("Initializing database...")
    
    # Initialize database tables
    init_db()
    logger.info("Database tables created.")
    
    # Check for sample data files
    sample_data_file = "cut_ai_survey_1224_responses.csv"
    
    if os.path.exists(sample_data_file):
        logger.info(f"Loading sample data from {sample_data_file}...")
        
        try:
            # Read and preprocess the data
            data = pd.read_csv(sample_data_file)
            processed_data = preprocess_data(data)
            
            # Load data to database
            records_added = load_survey_data_to_db(processed_data)
            logger.info(f"Added {records_added} sample records to database.")
            
        except Exception as e:
            logger.error(f"Error loading sample data: {str(e)}")
    else:
        logger.info(f"Sample data file {sample_data_file} not found. Skipping data import.")
    
    logger.info("Database initialization complete.")

if __name__ == "__main__":
    main()