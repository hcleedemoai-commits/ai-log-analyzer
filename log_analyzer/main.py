"""
ai-powered-log-analysis - Main entry point
"""

import os
import sys
from datetime import datetime
from config import Config

def main():
    """Main entry point."""
    print("Starting ai-powered-log-analysis...")
    
    try:
        Config.validate()
        print(f"Using model: {Config.MODEL}")
        
        # === YOUR CODE HERE ===
        print("Project is ready!")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
