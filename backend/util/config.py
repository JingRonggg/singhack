from functools import lru_cache
from dotenv import dotenv_values


@lru_cache(maxsize=1)
def load_config():
    """
    Loads only variables from .env and returns them as a dictionary.
    Uses LRU cache to memoize the result.
    Looks for .env in the backend directory.
    """
    # Find .env in the backend directory (where this file is located)

    return dotenv_values()
