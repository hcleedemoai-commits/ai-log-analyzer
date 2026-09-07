import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management."""
    
    # API Configuration
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct")
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    SAMPLE_LOGS_DIR = os.path.join(BASE_DIR, "sample_logs")

    # Default log file
    DEFAULT_LOG_FILE = os.path.join(SAMPLE_LOGS_DIR, "sample_logs.txt")

    @classmethod
    def validate(cls):
        """Check if API key is configured."""
        if not cls.API_KEY or cls.API_KEY == "your-api-key-here":
            raise ValueError("API key not found! Set OPENROUTER_API_KEY in .env")
        return True
