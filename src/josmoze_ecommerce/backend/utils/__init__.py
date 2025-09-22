"""
Utility functions and helpers for the Josmoze E-commerce application
"""

import os
import logging
from typing import Dict, Any, Optional

def get_env_var(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with optional default"""
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is required")
    return value

def setup_logging(level: str = "INFO") -> None:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_lead_score(lead_data: Dict[str, Any]) -> int:
    """Calculate lead score based on various factors"""
    score = 0
    
    # Email provided
    if lead_data.get('email'):
        score += 20
    
    # Phone provided
    if lead_data.get('phone'):
        score += 15
    
    if lead_data.get('company'):
        score += 25
    
    source = lead_data.get('source', '').lower()
    if source == 'website':
        score += 10
    elif source == 'referral':
        score += 30
    elif source == 'social_media':
        score += 15
    
    return min(score, 100)  # Cap at 100
