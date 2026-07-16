import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Whisper Configuration
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"  # Change to "cuda" if you have NVIDIA GPU

# Ollama Configuration
OLLAMA_MODEL = "llama2"      # Smarter 3.8GB model - perfect for deep content analysis
# OLLAMA_MODEL = "tinyllama"   # Lighter 637MB model - much faster but lower accuracy
OLLAMA_BASE_URL = "http://localhost:11434"

# Output Configuration
OUTPUT_DIR = "output"
OUTPUT_FORMATS = ["txt", "json"]

# Social Media Platforms
PLATFORMS = {
    "twitter": {"max_chars": 280},
    "instagram": {"max_chars": 2200},
    "linkedin": {"max_chars": 3000},
    "tiktok": {"max_chars": 150}
}

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)