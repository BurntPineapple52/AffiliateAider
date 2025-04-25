from typing import Dict, Optional
import re
from enum import Enum, auto
from praw.models import Subreddit
from praw.exceptions import PRAWException
from ..utils.error_handler import log_error
from ..utils.logging_utils import logger
from .rule_cache import RuleCache

class AffiliatePolicy(Enum):
    """Enum representing different affiliate link policies."""
    PROHIBITED = auto()
    ALLOWED = auto()
    RESTRICTED = auto()  # e.g. allowed but with conditions
    UNKNOWN = auto()

class RuleParser:
    """Parses subreddit rules and wikis to detect affiliate link policies."""
    
    DENIAL_PHRASES = [
        r"no\s+affiliate\s+links",
        r"no\s+referral\s+links",
        r"no\s+tracking\s+links", 
        r"prohibited\s+links",
        r"banned\s+links",
        r"no\s+promotion",
        r"no\s+self\s+promotion"
    ]
    
    APPROVAL_PHRASES = [
        r"affiliate\s+links\s+allowed",
        r"referral\s+links\s+ok",
        r"tracking\s+links\s+permitted",
        r"affiliate\s+policy"
    ]
    
    RESTRICTION_PHRASES = [
        r"only\s+approved\s+affiliates",
        r"must\s+be\s+disclosed",
        r"flair\s+required",
        r"mod\s+approval",
        r"restricted\s+links"
    ]

    def __init__(self, cache_ttl: int = 86400):
        self.denial_patterns = [re.compile(phrase, re.IGNORECASE) for phrase in self.DENIAL_PHRASES]
        self.approval_patterns = [re.compile(phrase, re.IGNORECASE) for phrase in self.APPROVAL_PHRASES]
        self.restriction_patterns = [re.compile(phrase, re.IGNORECASE) for phrase in self.RESTRICTION_PHRASES]
        self.cache = RuleCache(default_ttl=cache_ttl)

    def detect_affiliate_policy(self, subreddit: Subreddit) -> Dict[str, AffiliatePolicy]:
        """
        Detects the subreddit's affiliate link policy by checking rules and wiki.
        Uses caching to avoid repeated API calls for the same subreddit.
        
        Args:
            subreddit: The PRAW Subreddit object
            
        Returns:
            Dict containing policies from different sources and overall determination
        """
        # Check cache first
        cached = self.cache.get_rules(subreddit.display_name)
        if cached:
            logger.debug(f"Using cached rules for r/{subreddit.display_name}")
            return cached

        policies = {
            'rules_policy': self._check_rules(subreddit),
            'wiki_policy': self._check_wiki(subreddit),
            'overall_policy': AffiliatePolicy.UNKNOWN
        }

        # Cache the results
        self.cache.set_rules(subreddit.display_name, policies)
        
        # Determine overall policy based on available information
        if policies['rules_policy'] != AffiliatePolicy.UNKNOWN:
            policies['overall_policy'] = policies['rules_policy']
        elif policies['wiki_policy'] != AffiliatePolicy.UNKNOWN:
            policies['overall_policy'] = policies['wiki_policy']
            
        return policies
            
    def _check_rules(self, subreddit: Subreddit) -> AffiliatePolicy:
        """Check the subreddit rules for affiliate policy information."""
        try:
            rules = subreddit.rules()
            if not rules:
                logger.debug(f"No rules found for subreddit: {subreddit.display_name}")
                return AffiliatePolicy.UNKNOWN
                
            rule_text = str(rules).lower()
            
            # Check for approval phrases first
            for pattern in self.approval_patterns:
                if pattern.search(rule_text):
                    logger.info(f"Detected explicit affiliate link allowance in r/{subreddit.display_name} rules")
                    return AffiliatePolicy.ALLOWED
                    
            # Then check for restrictions
            for pattern in self.restriction_patterns:
                if pattern.search(rule_text):
                    logger.info(f"Detected affiliate link restrictions in r/{subreddit.display_name} rules")
                    return AffiliatePolicy.RESTRICTED
                    
            # Finally check for denials
            for pattern in self.denial_patterns:
                if pattern.search(rule_text):
                    logger.info(f"Detected affiliate link prohibition in r/{subreddit.display_name} rules")
                    return AffiliatePolicy.PROHIBITED
                    
            logger.debug(f"No clear affiliate policy found in r/{subreddit.display_name} rules")
            return AffiliatePolicy.UNKNOWN
            
        except PRAWException as e:
            log_error(f"Failed to parse rules for r/{subreddit.display_name}: {str(e)}")
            return AffiliatePolicy.UNKNOWN
            
    def _check_wiki(self, subreddit: Subreddit) -> AffiliatePolicy:
        """Check the subreddit wiki for affiliate policy information."""
        try:
            wiki_pages = subreddit.wiki
            if not wiki_pages:
                return AffiliatePolicy.UNKNOWN
                
            # Check common wiki page names for policies
            for page_name in ['rules', 'faq', 'policies', 'affiliate']:
                try:
                    wiki_text = str(wiki_pages[page_name].content_md).lower()
                    
                    # Check for approval phrases first
                    for pattern in self.approval_patterns:
                        if pattern.search(wiki_text):
                            logger.info(f"Detected explicit affiliate link allowance in r/{subreddit.display_name} wiki")
                            return AffiliatePolicy.ALLOWED
                            
                    # Then check for restrictions
                    for pattern in self.restriction_patterns:
                        if pattern.search(wiki_text):
                            logger.info(f"Detected affiliate link restrictions in r/{subreddit.display_name} wiki")
                            return AffiliatePolicy.RESTRICTED
                            
                    # Finally check for denials
                    for pattern in self.denial_patterns:
                        if pattern.search(wiki_text):
                            logger.info(f"Detected affiliate link prohibition in r/{subreddit.display_name} wiki")
                            return AffiliatePolicy.PROHIBITED
                            
                except PRAWException:
                    continue
                    
            return AffiliatePolicy.UNKNOWN
                    
        except PRAWException as e:
            log_error(f"Failed to check wiki for r/{subreddit.display_name}: {str(e)}")
            return AffiliatePolicy.UNKNOWN
