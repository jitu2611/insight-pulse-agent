import os
import yaml
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load secret environment variables
load_dotenv()

class Persona(BaseModel):
    name: str
    role: str
    interests: List[str]
    tone: str

class Feed(BaseModel):
    name: str
    url: str

class AIConfig(BaseModel):
    provider: str
    model_id: str
    temperature: float = 0.2

class NotificationConfig(BaseModel):
    enabled: bool
    ntfy_topic: str
    brief_only: bool = True

class Config(BaseModel):
    persona: Persona
    feeds: List[str] | List[dict] # Allow both simple URLs or dicts
    ai: AIConfig
    notifications: NotificationConfig

def load_config() -> Config:
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found! Check your project root.")
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    
    # Process feeds if they are objects
    processed_feeds = []
    for f in data.get("feeds", []):
        if isinstance(f, dict):
            processed_feeds.append(f)
        else:
            processed_feeds.append({"name": "Uncategorized Feed", "url": f})
    
    data["feeds"] = processed_feeds
    return Config(**data)

# Export a global instance
config = load_config()
