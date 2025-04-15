#!/usr/bin/env python3
"""
Database backup and restore utility for the CUT AI Adoption Analytics Platform.
"""

import os
import sys
import json
import argparse
import sqlite3
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from database import (
    Survey, Prediction, Insight, SessionLocal, 
    load_survey_data_to_db, save_predictions_to_db, save_insight_to_db
)
from loggers import get_logger

# Set up logger
logger = get_logger("db_backup")

def backup_database(output_dir="./data/backups"):
    """
    Backup the database tables to JSON files.
    
    Args:
        output_dir (str): Directory to store the backup files
        
    Returns:
        dict: Backup statistics
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create backup timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(output_dir, f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Backup surveys
        surveys = db.query(Survey).all()
        survey_data = []
        
        for survey in surveys:
            survey_data.append({
                "id": survey.id,
                "email": survey.email,
                "level_of_study": survey.level_of_study,
                "faculty": survey.faculty,
                "ai_familiarity": survey.ai_familiarity,
                "used_ai_tools": survey.used_ai_tools,
                "tools_used": survey.tools_used,
                "usage_frequency": survey.usage_frequency,
                "challenges": survey.challenges,
                "helpful_tools_needed": survey.helpful_tools_needed,
                "improves_learning": survey.improves_learning,
                "suggestions": survey.suggestions,
                "tools_count": survey.tools_count,
                "challenges_count": survey.challenges_count
            })
        
        with open(os.path.join(backup_dir, "surveys.json"), "w") as f:
            json.dump(survey_data, f, indent=2)
        
        # Backup predictions
        predictions = db.query(Prediction).all()
        prediction_data = []
        
        for prediction in predictions:
            prediction_data.append({
                "id": prediction.id,
                "survey_id": prediction.survey_id,
                "adoption_probability": prediction.adoption_probability,
                "model_version": prediction.model_version,
                "created_at": prediction.created_at
            })
        
        with open(os.path.join(backup_dir, "predictions.json"), "w") as f:
            json.dump(prediction_data, f, indent=2)
        
        # Backup insights
        insights = db.query(Insight).all()
        insight_data = []
        
        for insight in insights:
            insight_data.append({
                "id": insight.id,
                "batch_id": insight.batch_id,
                "insight_text": insight.insight_text,
                "category": insight.category,
                "created_at": insight.created_at
            })
        
        with open(os.path.join(backup_dir, "insights.json"), "w") as f:
            json.dump(insight_data, f, indent=2)
        
        # Create backup info file
        backup_info = {
            "timestamp": timestamp,
            "surveys_count": len(survey_data),
            "predictions_count": len(prediction_data),
            "insights_count": len(insight_data)
        }
        
        with open(os.path.join(backup_dir, "backup_info.json"), "w") as f:
            json.dump(backup_info, f, indent=2)
        
        logger.info(f"Backup completed: {backup_dir}")
        logger.info(f"Backed up {len(survey_data)} surveys, {len(prediction_data)} predictions, {len(insight_data)} insights")
        
        return backup_info
        
    finally:
        db.close()

def restore_database(backup_dir):
    """
    Restore the database from backup files.
    
    Args:
        backup_dir (str): Directory containing the backup files
        
    Returns:
        dict: Restore statistics
    """
    logger.info(f"Restoring database from {backup_dir}...")
    
    # Check if backup directory exists
    if not os.path.exists(backup_dir):
        logger.error(f"Backup directory {backup_dir} does not exist")
        return None
    
    # Check for required backup files
    required_files = ["surveys.json", "predictions.json", "insights.json", "backup_info.json"]
    for file in required_files:
        if not os.path.exists(os.path.join(backup_dir, file)):
            logger.error(f"Required backup file {file} not found in {backup_dir}")
            return None
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data (optional, use with caution)
        if input("Do you want to clear existing data? (y/n): ").lower() == "y":
            db.query(Prediction).delete()
            db.query(Insight).delete()
            db.query(Survey).delete()
            db.commit()
            logger.info("Existing data cleared")
        
        # Load backup data
        with open(os.path.join(backup_dir, "surveys.json"), "r") as f:
            survey_data = json.load(f)
        
        with open(os.path.join(backup_dir, "predictions.json"), "r") as f:
            prediction_data = json.load(f)
        
        with open(os.path.join(backup_dir, "insights.json"), "r") as f:
            insight_data = json.load(f)
        
        # Restore surveys
        survey_count = 0
        for data in survey_data:
            existing = db.query(Survey).filter_by(email=data["email"]).first()
            if not existing:
                survey = Survey(
                    email=data["email"],
                    level_of_study=data["level_of_study"],
                    faculty=data["faculty"],
                    ai_familiarity=data["ai_familiarity"],
                    used_ai_tools=data["used_ai_tools"],
                    tools_used=data["tools_used"],
                    usage_frequency=data["usage_frequency"],
                    challenges=data["challenges"],
                    helpful_tools_needed=data["helpful_tools_needed"],
                    improves_learning=data["improves_learning"],
                    suggestions=data["suggestions"],
                    tools_count=data["tools_count"],
                    challenges_count=data["challenges_count"]
                )
                db.add(survey)
                survey_count += 1
        
        db.commit()
        logger.info(f"Restored {survey_count} surveys")
        
        # Restore predictions
        prediction_count = 0
        for data in prediction_data:
            prediction = Prediction(
                survey_id=data["survey_id"],
                adoption_probability=data["adoption_probability"],
                model_version=data["model_version"],
                created_at=data["created_at"]
            )
            db.add(prediction)
            prediction_count += 1
        
        db.commit()
        logger.info(f"Restored {prediction_count} predictions")
        
        # Restore insights
        insight_count = 0
        for data in insight_data:
            insight = Insight(
                batch_id=data["batch_id"],
                insight_text=data["insight_text"],
                category=data["category"],
                created_at=data["created_at"]
            )
            db.add(insight)
            insight_count += 1
        
        db.commit()
        logger.info(f"Restored {insight_count} insights")
        
        # Return restore statistics
        restore_info = {
            "surveys_restored": survey_count,
            "predictions_restored": prediction_count,
            "insights_restored": insight_count,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        logger.info("Restore completed")
        return restore_info
        
    finally:
        db.close()

def list_backups(backup_dir="./data/backups"):
    """
    List available database backups.
    
    Args:
        backup_dir (str): Directory containing the backup directories
        
    Returns:
        list: Available backup directories
    """
    if not os.path.exists(backup_dir):
        logger.error(f"Backup directory {backup_dir} does not exist")
        return []
    
    backups = []
    
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.isdir(item_path) and item.startswith("backup_"):
            info_file = os.path.join(item_path, "backup_info.json")
            if os.path.exists(info_file):
                with open(info_file, "r") as f:
                    info = json.load(f)
                
                backups.append({
                    "dir": item,
                    "path": item_path,
                    "timestamp": info["timestamp"],
                    "surveys_count": info["surveys_count"],
                    "predictions_count": info["predictions_count"],
                    "insights_count": info["insights_count"]
                })
    
    # Sort by timestamp (most recent first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return backups

def main():
    """Main function for the backup utility."""
    parser = argparse.ArgumentParser(description="Database backup and restore utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup the database")
    backup_parser.add_argument("--output-dir", "-o", default="./data/backups", help="Output directory for the backup")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore the database from backup")
    restore_parser.add_argument("--backup-dir", "-b", required=True, help="Backup directory to restore from")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")
    list_parser.add_argument("--backup-dir", "-b", default="./data/backups", help="Directory containing the backups")
    
    args = parser.parse_args()
    
    if args.command == "backup":
        backup_database(args.output_dir)
    elif args.command == "restore":
        restore_database(args.backup_dir)
    elif args.command == "list":
        backups = list_backups(args.backup_dir)
        if backups:
            print("\nAvailable backups:")
            for i, backup in enumerate(backups):
                print(f"{i+1}. {backup['dir']} - Surveys: {backup['surveys_count']}, Predictions: {backup['predictions_count']}, Insights: {backup['insights_count']}")
        else:
            print("No backups found")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()