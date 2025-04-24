from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class KeywordState(Enum):
    """Track the processing state of keywords"""
    NEW = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class TrackedKeyword:
    """Data class for tracking keyword metadata"""
    keyword: str
    state: KeywordState = KeywordState.NEW
    last_processed: datetime = None
    processed_count: int = 0
    failed_count: int = 0

class KeywordTracker:
    """Manages the tracking and state of keywords"""
    
    def __init__(self):
        self.keywords: Dict[str, TrackedKeyword] = {}
        
    def add_keyword(self, keyword: str) -> None:
        """Add a new keyword to track"""
        if keyword not in self.keywords:
            self.keywords[keyword] = TrackedKeyword(keyword=keyword)
            
    def update_state(self, keyword: str, state: KeywordState) -> None:
        """Update the state of a tracked keyword"""
        if keyword in self.keywords:
            self.keywords[keyword].state = state
            self.keywords[keyword].last_processed = datetime.now()
            
            if state == KeywordState.COMPLETED:
                self.keywords[keyword].processed_count += 1
            elif state == KeywordState.FAILED:
                self.keywords[keyword].failed_count += 1
                
    def get_keywords_by_state(self, state: KeywordState) -> List[TrackedKeyword]:
        """Get all keywords in a specific state"""
        return [kw for kw in self.keywords.values() if kw.state == state]
