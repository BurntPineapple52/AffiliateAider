import re
import time
from typing import List, Optional
from urllib.parse import urlparse

class SERPParser:
    _last_request_time: Optional[float] = None
    MIN_REQUEST_INTERVAL = 2.0  # 2 seconds between requests minimum
    """
    Parser for extracting Reddit URLs from search engine results.
    """

    REDDIT_DOMAINS = {
        'www.reddit.com',
        'reddit.com',
        'old.reddit.com',
        'np.reddit.com',
        'ssl.reddit.com'
    }

    @classmethod
    def _enforce_rate_limit(cls):
        """Enforce minimum time between API requests."""
        if cls._last_request_time is not None:
            elapsed = time.time() - cls._last_request_time
            if elapsed < cls.MIN_REQUEST_INTERVAL:
                time.sleep(cls.MIN_REQUEST_INTERVAL - elapsed)
        cls._last_request_time = time.time()

    @classmethod
    def extract_reddit_urls(cls, search_results: List[dict]) -> List[str]:
        cls._enforce_rate_limit()
        """
        Extract and validate Reddit URLs from search engine results.

        Args:
            search_results: List of dictionaries containing search result items

        Returns:
            List of cleaned Reddit URLs
        """
        reddit_urls = []
        
        for result in search_results:
            if not result.get('link'):
                continue
                
            parsed_url = urlparse(result['link'])
            if parsed_url.netloc in cls.REDDIT_DOMAINS:
                # Standardize URL scheme and strip tracking parameters
                clean_url = f"https://{parsed_url.netloc}{parsed_url.path}"
                reddit_urls.append(clean_url)
                
        return reddit_urls

    @classmethod
    def extract_thread_ids(cls, reddit_urls: List[str]) -> List[str]:
        """
        Extract Reddit thread IDs from URLs.
        Returns empty list for non-thread URLs.
        """
        thread_ids = []
        thread_pattern = re.compile(r'/comments/([a-z0-9]+)/')
        
        for url in reddit_urls:
            match = thread_pattern.search(url)
            if match:
                thread_ids.append(match.group(1))
                
        return thread_ids
