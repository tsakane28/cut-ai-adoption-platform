#!/usr/bin/env python3
"""
Docker setup utility for CUT AI Adoption Analytics Platform
"""

import os
import subprocess
import sys
import time

def print_colored(text, color):
    """Print colored text"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_docker_installed():
    """Check if Docker is installed"""
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_docker_compose_installed():
    """Check if Docker Compose is installed"""
    try:
        subprocess.run(["docker-compose", "--version"], check=True, stdout=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def build_docker_images():
    """Build Docker images"""
    print_colored("Building Docker images...", "blue")
    subprocess.run(["docker-compose", "build"], check=True)
    print_colored("Docker images built successfully!", "green")

def start_containers():
    """Start Docker containers"""
    print_colored("Starting Docker containers...", "blue")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    print_colored("Docker containers started successfully!", "green")

def stop_containers():
    """Stop Docker containers"""
    print_colored("Stopping Docker containers...", "yellow")
    subprocess.run(["docker-compose", "down"], check=True)
    print_colored("Docker containers stopped successfully!", "green")

def restart_containers():
    """Restart Docker containers"""
    stop_containers()
    time.sleep(2)
    start_containers()

def show_logs():
    """Show Docker container logs"""
    print_colored("Showing logs (press Ctrl+C to exit):", "blue")
    try:
        subprocess.run(["docker-compose", "logs", "-f"], check=True)
    except KeyboardInterrupt:
        print_colored("\nExited logs view", "yellow")

def init_database():
    """Initialize the database"""
    print_colored("Initializing database...", "blue")
    subprocess.run([
        "docker-compose", "exec", "app", 
        "python", "-c", "from database import init_db; init_db()"
    ], check=True)
    print_colored("Database initialized successfully!", "green")

def main():
    """Main function"""
    print_colored("=== CUT AI Adoption Analytics Platform - Docker Setup ===", "cyan")
    
    # Check Docker installation
    if not check_docker_installed():
        print_colored("Error: Docker is not installed. Please install Docker first.", "red")
        sys.exit(1)
    
    # Check Docker Compose installation
    if not check_docker_compose_installed():
        print_colored("Error: Docker Compose is not installed. Please install Docker Compose first.", "red")
        sys.exit(1)
    
    while True:
        print("\nOptions:")
        print("1. Build and start containers")
        print("2. Stop containers")
        print("3. Restart containers")
        print("4. Show container logs")
        print("5. Initialize database")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            build_docker_images()
            start_containers()
            print_colored("\nApplication is running at http://localhost:5000", "green")
        elif choice == "2":
            stop_containers()
        elif choice == "3":
            restart_containers()
            print_colored("\nApplication is running at http://localhost:5000", "green")
        elif choice == "4":
            show_logs()
        elif choice == "5":
            init_database()
        elif choice == "0":
            print_colored("Exiting...", "yellow")
            sys.exit(0)
        else:
            print_colored("Invalid choice. Please try again.", "red")

if __name__ == "__main__":
    main()