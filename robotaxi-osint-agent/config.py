"""
Configuration settings for the Robotaxi OSINT Agent.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application Settings
    SUBREDDITS: List[str] = ["TeslaLounge", "SelfDrivingCars", "teslamotors"]
    OUTPUT_FILE: str = os.getenv("OUTPUT_FILE", "candidates.json")
    STATE_FILE: str = os.getenv("STATE_FILE", "state.json")
    
    # Keywords for filtering
    KEYWORDS: List[str] = [
        "robotaxi",
        "cybercab",
        "camouflage",
        "lidar",
        "test vehicle",
        "prototype",
        "manufacturer plate",
        "mfg plate",
        "dst plate"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True
