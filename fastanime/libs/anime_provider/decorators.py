import functools
import logging
import os

logger = logging.getLogger(__name__)


def debug_provider(provider_name: str):
    def _provider_function_decorator(provider_function):
        @functools.wraps(provider_function)
        def _provider_function_wrapper(*args, **kwargs):
            if not os.environ.get("FASTANIME_DEBUG"):
                try:
                    return provider_function(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[{provider_name}@{provider_function.__name__}]: {e}")
            else:
                return provider_function(*args, **kwargs)

        return _provider_function_wrapper

    return _provider_function_decorator


def ensure_internet_connection(provider_function):
    @functools.wraps(provider_function)
    def _wrapper(*args, **kwargs):
        import requests

        try:
            requests.get("https://google.com", timeout=5)
        except requests.ConnectionError:
            from sys import exit

            print("You are not connected to the internet;Aborting...")
            exit(1)
        return provider_function(*args, **kwargs)

    return _wrapper
