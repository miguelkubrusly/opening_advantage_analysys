import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime


def get_api_key(env_path="./.env") -> None | str:
    """
    Retrieves the 'api_key' from the .env file.

    Args:
        env_path (str): Path to the .env file.

    Returns:
        str or None: The API key value, or None if not found.
    """
    load_dotenv(dotenv_path=env_path)
    api_key: str | None = os.getenv("api_key")
    if api_key is None:
        print("api_key não encontrada.")
    return api_key


def get_lichess_token(env_path: str = "./.env") -> None | str:
    """
    Retrieves the 'LICHESS_API_TOKEN' from the .env file.

    Args:
        env_path (str): Path to the .env file.

    Returns:
        str or None: The token value, or None if not found.
    """
    load_dotenv(dotenv_path=env_path)
    token: str | None = os.getenv("LICHESS_API_TOKEN")
    if token is None:
        # Token is optional for public games, but print a hint once.
        print("LICHESS_API_TOKEN não encontrado (opcional para jogos públicos).")
    return token


def ensure_directory_exists(path: str) -> None:
    """
    Ensures that the specified directory exists.

    Args:
        path (str): The directory path to ensure.
    """
    Path(path).expanduser().resolve().mkdir(parents=True, exist_ok=True)


def get_timestamp(format: str = "%Y%m%d_%H%M") -> str:

    return datetime.now().strftime(format)
