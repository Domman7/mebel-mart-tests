"""
Retry utilities for unstable operations
"""

import time
import allure
from functools import wraps


def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    """
    Decorator for retrying failed operations

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        allure.attach(
                            f"Attempt {attempt + 1} failed: {str(e)}. Retrying...",
                            name=f"Retry info for {func.__name__}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator