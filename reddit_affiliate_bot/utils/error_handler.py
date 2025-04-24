from loguru import logger
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')

class ErrorHandler:
    """Centralized error handling for the bot application."""
    
    @staticmethod
    def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to wrap functions with standardized error handling.
        
        Args:
            func: The function to wrap with error handling
            
        Returns:
            The wrapped function
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise  # Re-raise after logging to allow calling code to handle
        return wrapper
        
    @staticmethod
    def silent_handle_errors(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to silently handle and log errors without raising.
        
        Args:
            func: The function to wrap with error handling
            
        Returns:
            The wrapped function that returns None on error
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Silenced error in {func.__name__}: {str(e)}")
                return None
        return wrapper
