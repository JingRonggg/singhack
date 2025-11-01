from functools import lru_cache
from dotenv import dotenv_values


@lru_cache(maxsize=1)
def load_config():
    """
    Loads only variables from .env and returns them as a dictionary.
    Uses LRU cache to memoize the result.
    """
    return dotenv_values()
