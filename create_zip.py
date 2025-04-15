#!/usr/bin/env python3
"""
Script to create a ZIP file of the application for easy distribution.
"""

import os
import zipfile
import argparse
import time
from datetime import datetime

def create_app_zip(output_name=None, include_data=True):
    """
    Create a ZIP file of the application.
    
    Args:
        output_name (str, optional): Name of the output ZIP file
        include_data (bool): Whether to include data files
        
    Returns:
        str: Path to the created ZIP file
    """
    # Define the output filename
    if output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"app_download_{timestamp}.zip"
    elif not output_name.endswith(".zip"):
        output_name += ".zip"
    
    # Define files and directories to exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".vscode",
        ".idea",
        "*.log",
        "logs",
        "*.zip",
        ".env",
        ".gitignore",
        ".dockerignore",
    ]
    
    if not include_data:
        exclude_patterns.append("*.csv")
        exclude_patterns.append("data")
    
    # Create the ZIP file
    with zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(d == pat.replace("*", "") for pat in exclude_patterns)]
            
            for file in files:
                # Skip files matching exclude patterns
                if any(file.endswith(pat.replace("*", "")) for pat in exclude_patterns if "*" in pat):
                    continue
                if any(file == pat for pat in exclude_patterns if "*" not in pat):
                    continue
                if file == output_name:  # Skip the output zip file itself
                    continue
                
                # Add file to ZIP with current timestamp to avoid issues with old files
                file_path = os.path.join(root, file)
                
                # Create a ZipInfo object to set the date
                info = zipfile.ZipInfo(file_path[2:])  # Remove leading "./"
                info.date_time = time.localtime(time.time())[:6]
                info.compress_type = zipfile.ZIP_DEFLATED
                
                # Read the file and add it to the ZIP
                with open(file_path, 'rb') as f:
                    zipf.writestr(info, f.read())
    
    print(f"ZIP file created: {output_name}")
    return output_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a ZIP file of the application.")
    parser.add_argument("--output", "-o", help="Name of the output ZIP file")
    parser.add_argument("--no-data", action="store_true", help="Exclude data files")
    
    args = parser.parse_args()
    create_app_zip(args.output, not args.no_data)