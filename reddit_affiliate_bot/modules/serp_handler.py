import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build

class SERPHandler:
    """Handles search engine results parsing and processing"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service = build("customsearch", "v1", developerKey=api_key)
        self.logger = logging.getLogger(__name__)

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Perform a search and return parsed results"""
        try:
            res = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results
            ).execute()
            return res.get('items', [])
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {str(e)}")
            return []

    def parse_results(self, results: List[Dict]) -> List[Dict]:
        """Parse raw search results into structured data"""
        parsed = []
        for item in results:
            parsed.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            })
        return parsed
