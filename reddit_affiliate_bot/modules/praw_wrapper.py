import time
import praw
from loguru import logger
from typing import Optional, Dict, Any, List
from datetime import datetime
from config import RedditConfig

class RedditWrapper:
    """Wrapper class to handle PRAW interactions with Reddit API"""
    
    def __init__(self, config: RedditConfig):
        """
        Initialize PRAW Reddit instance with RedditConfig
        
        Args:
            config (RedditConfig): Configuration dataclass containing Reddit credentials
        """
        self.config = config
        self._initialize_client()
        logger.success("Successfully initialized PRAW Reddit client")

    def _initialize_client(self):
        """Initialize PRAW client with appropriate auth method"""
        try:
            proxy_config = self.config.proxy
            proxy_enabled = proxy_config.enabled if proxy_config else False
            
            # Set up proxy config if enabled
            proxy_settings = {}
            if proxy_enabled:
                proxy_url = f"{proxy_config.protocol}://"
                if proxy_config.username and proxy_config.password:
                    proxy_url += f"{proxy_config.username}:{proxy_config.password}@"
                proxy_url += f"{proxy_config.host}:{proxy_config.port}"
                proxy_settings = {'https': proxy_url}
                logger.info(f"Using proxy: {proxy_url}")

            if self.config.auth_method == 'refresh_token' and self.config.refresh_token:
                self.reddit = praw.Reddit(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                    user_agent=self.config.user_agent,
                    refresh_token=self.config.refresh_token,
                    proxies=proxy_settings,
                    requestor_kwargs={'proxies': proxy_settings}
                )
            else:
                self.reddit = praw.Reddit(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                    user_agent=self.config.user_agent,
                    username=self.config.username,
                    password=self.config.password,
                    proxies=proxy_settings,
                    requestor_kwargs={'proxies': proxy_settings}
                )
            
            # Verify auth immediately
            self.reddit.user.me()
            logger.success("Successfully authenticated with Reddit")
        except praw.exceptions.PRAWException as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise RuntimeError(f"Reddit authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise RuntimeError(f"Unexpected authentication error: {str(e)}")

    def refresh_auth(self, max_attempts: int = 3) -> bool:
        """Refresh OAuth token if using refresh_token auth
        
        Args:
            max_attempts (int): Maximum number of refresh attempts
            
        Returns:
            bool: True if refresh succeeded, False otherwise
        """
        if self.config.auth_method != 'refresh_token':
            return True
            
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Attempting token refresh (attempt {attempt}/{max_attempts})")
                self._initialize_client()
                logger.success("Successfully refreshed OAuth token")
                return True
            except Exception as e:
                logger.error(f"Refresh attempt {attempt} failed: {str(e)}")
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        logger.error(f"Failed to refresh token after {max_attempts} attempts")
        return False

    def get_comment(self, comment_id: str) -> Optional[praw.models.Comment]:
        """Fetch a comment by ID"""
        try:
            comment = self.reddit.comment(id=comment_id)
            logger.debug(f"Fetched comment {comment_id}")
            return comment
        except Exception as e:
            logger.error(f"Failed to fetch comment {comment_id}: {str(e)}")
            return None

    def get_submission(self, submission_id: str) -> Optional[praw.models.Submission]:
        """Fetch a submission by ID"""
        try:
            submission = self.reddit.submission(id=submission_id)
            logger.debug(f"Fetched submission {submission_id}")
            return submission
        except Exception as e:
            logger.error(f"Failed to fetch submission {submission_id}: {str(e)}")
            return None

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """Post a reply to a comment
        
        Args:
            comment_id (str): ID of comment to reply to
            text (str): Text of reply
            
        Returns:
            bool: True if reply was successful, False otherwise
        """
        if not self.is_authenticated():
            logger.error(f"Cannot reply to {comment_id} - not authenticated")
            return False

        try:
            comment = self.get_comment(comment_id)
            if not comment:
                logger.error(f"Comment {comment_id} not found")
                return False
                
            # Check rate limit
            remaining = float(self.reddit.auth.limits['remaining'])
            if remaining < 2:  # Leave some buffer
                wait_time = float(self.reddit.auth.limits['reset_timestamp']) - time.time()
                logger.warning(f"Rate limit hit, waiting {wait_time:.1f}s before posting")
                time.sleep(wait_time + 1)
                
            reply = comment.reply(text)
            logger.success(f"Posted reply to {comment_id}: https://reddit.com{reply.permalink}")
            return True
            
        except praw.exceptions.RedditAPIException as e:
            for sub_err in e.items:
                logger.error(f"Reddit API error replying to {comment_id}: {sub_err.error_type}: {sub_err.message}")
            return False
        except praw.exceptions.ClientException as e:
            logger.error(f"PRAW client error replying to {comment_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error replying to {comment_id}: {str(e)}", exc_info=True)
            return False

    def get_subreddit_rules(self, subreddit_name: str) -> Optional[Dict[str, Any]]:
        """Fetch complete rule set for a subreddit including removal reasons"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get primary rules
            rules = []
            for rule in subreddit.rules:
                rules.append({
                    'short_name': rule.short_name,
                    'description': rule.description,
                    'violation_reason': rule.violation_reason,
                    'created_utc': datetime.fromtimestamp(rule.created_utc),
                    'priority': rule.priority
                })

            # Get moderation rules/removal reasons
            removal_reasons = []
            if hasattr(subreddit, 'mod'):  # Only available to moderators
                try:
                    for reason in subreddit.mod.removal_reasons:
                        removal_reasons.append({
                            'id': reason.id,
                            'title': reason.title,
                            'message': reason.message
                        })
                except Exception as e:
                    logger.warning(f"Couldn't fetch removal reasons for {subreddit_name}: {str(e)}")

            result = {
                'name': subreddit.display_name,
                'rules': rules,
                'removal_reasons': removal_reasons,
                'public_description': subreddit.public_description,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                'subscribers': subreddit.subscribers
            }

            logger.debug(f"Fetched complete ruleset for subreddit {subreddit_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch rules for {subreddit_name}: {str(e)}")
            return None

    def get_new_submissions(self, subreddit_name: str, limit: int = 10) -> List[praw.models.Submission]:
        """Fetch new submissions from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = list(subreddit.new(limit=limit))
            logger.debug(f"Fetched {len(submissions)} new submissions from {subreddit_name}")
            return submissions
        except Exception as e:
            logger.error(f"Failed to fetch submissions from {subreddit_name}: {str(e)}")
            return []

    def get_hot_submissions(self, subreddit_name: str, limit: int = 10) -> List[praw.models.Submission]:
        """Fetch hot submissions from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = list(subreddit.hot(limit=limit))
            logger.debug(f"Fetched {len(submissions)} hot submissions from {subreddit_name}")
            return submissions
        except Exception as e:
            logger.error(f"Failed to fetch hot submissions from {subreddit_name}: {str(e)}")
            return []

    def get_comments_from_submission(self, submission_id: str, limit: int = 20) -> List[praw.models.Comment]:
        """Fetch comments from a submission"""
        try:
            submission = self.get_submission(submission_id)
            if not submission:
                return []
                
            submission.comments.replace_more(limit=0)  # Remove MoreComments objects
            comments = list(submission.comments.list())[:limit]
            logger.debug(f"Fetched {len(comments)} comments from submission {submission_id}")
            return comments
        except Exception as e:
            logger.error(f"Failed to fetch comments from submission {submission_id}: {str(e)}")
            return []

    def check_proxy_health(self) -> bool:
        """Check latency and reliability of current proxy"""
        if not self.config.proxy or not self.config.proxy.enabled:
            return True
            
        try:
            start_time = time.time()
            subreddit = self.reddit.subreddit('all')
            _ = subreddit.description  # Simple API call to test connectivity
            response_time = time.time() - start_time
            
            # Update proxy stats through proxy manager if available
            if hasattr(self, 'proxy_manager'):
                proxy_id = self._get_current_proxy_id()
                self.proxy_manager.update_stats(proxy_id, True, response_time)
            
            return response_time < 2.0  # Threshold in seconds
        except Exception as e:
            logger.error(f"Proxy health check failed: {str(e)}")
            if hasattr(self, 'proxy_manager') and hasattr(self.config, 'proxy'):
                proxy_id = self._get_current_proxy_id()
                self.proxy_manager.update_stats(proxy_id, False, 0)
            return False

    def is_authenticated(self, retry: bool = True) -> bool:
        """Check if the client is properly authenticated with optional retry
        
        Args:
            retry (bool): Whether to attempt refresh if auth fails
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            self.reddit.user.me()
            return True
        except praw.exceptions.PRAWException as e:
            logger.warning(f"Auth check failed: {str(e)}")
            if retry and self.config.auth_method == 'refresh_token':
                logger.info("Attempting token refresh...")
                return self.refresh_auth()
            return False
        except Exception as e:
            logger.error(f"Unexpected error during auth check: {str(e)}")
            return False

    def search_submissions(self, query: str, subreddit: str = None, limit: int = 10) -> List[praw.models.Submission]:
        """Search for submissions matching query"""
        try:
            if subreddit:
                results = list(self.reddit.subreddit(subreddit).search(query, limit=limit))
            else:
                results = list(self.reddit.subreddit("all").search(query, limit=limit))
                
            logger.debug(f"Found {len(results)} submissions matching query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search submissions: {str(e)}")
            return []
