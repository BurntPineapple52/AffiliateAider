from loguru import logger
import sys

def configure_logging():
    """Configure Loguru logger with standard settings"""
    
    logger.remove()  # Remove default handler
    
    # Add stdout handler with color and formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Add optional file handler
    logger.add(
        "logs/app.log",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        level="DEBUG"
    )
