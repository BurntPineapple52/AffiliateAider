import csv
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CSVKeywordSource:
    """Handles loading keywords from a CSV file source."""
    
    def __init__(self, file_path: str):
        """
        Initialize CSV keyword source.
        
        Args:
            file_path: Path to CSV file containing keywords
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Keyword CSV file not found: {file_path}")

    def load_keywords(self) -> List[Dict[str, str]]:
        """
        Load keywords from CSV file.
        
        Returns:
            List of keyword dictionaries with their metadata
        """
        keywords = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    keywords.append(dict(row))
            logger.info(f"Loaded {len(keywords)} keywords from {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to load keywords from {self.file_path}: {str(e)}")
            raise
        
        return keywords
