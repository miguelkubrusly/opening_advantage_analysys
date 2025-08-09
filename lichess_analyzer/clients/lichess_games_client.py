import requests
from typing import Iterable


def fetch_user_games_pgn(
    username: str, maximum_games: int, speeds: list[str], api_token: str | None
) -> Iterable[str]:
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": maximum_games,
        "moves": True,
        "tags": True,
        "evals": False,
        "clocks": False,
        "opening": True,
        "perfType": ",".join(speeds),
    }
    headers = {"Accept": "application/x-chess-pgn"}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    response = requests.get(url, params=params, headers=headers, timeout=60)
    response.raise_for_status()
    # A resposta vem como um PGNão (vários jogos concatenados). Separe por linhas em branco.
    raw = response.text.strip()
    for chunk in raw.split("\n\n\n"):
        chunk = chunk.strip()
        if chunk:
            yield chunk
