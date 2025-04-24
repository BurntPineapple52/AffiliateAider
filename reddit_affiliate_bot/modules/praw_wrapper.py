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
        try:
            self.reddit = praw.Reddit(
                client_id=config.client_id,
                client_secret=config.client_secret,
                user_agent=config.user_agent,
                username=config.username,
                password=config.password
            )
            logger.success("Successfully initialized PRAW Reddit client")
        except Exception as e:
            logger.error(f"Failed to initialize PRAW client: {str(e)}")
            raise

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
        """Post a reply to a comment"""
        try:
            comment = self.get_comment(comment_id)
            if comment:
                reply = comment.reply(text)
                logger.success(f"Posted reply to comment {comment_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to reply to comment {comment_id}: {str(e)}")
            return False

    def get_subreddit_rules(self, subreddit_name: str) -> Optional[Dict[str, Any]]:
        """Fetch rules for a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            rules = []
            for rule in subreddit.rules:
                rules.append({
                    'short_name': rule.short_name,
                    'description': rule.description,
                    'created_utc': datetime.fromtimestamp(rule.created_utc),
                })
            logger.debug(f"Fetched rules for subreddit {subreddit_name}")
            return rules
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
