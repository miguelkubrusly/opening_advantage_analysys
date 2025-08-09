import requests

EXPLORER_URL = "https://explorer.lichess.ovh/lichess"


def move_exists_in_theory(
    fen_before_move: str, next_move_uci: str, speeds: list[str], minimum_games: int
) -> bool:
    params = {
        "variant": "standard",
        "fen": fen_before_move,
        # "moves": 0,
        "speeds": ",".join(speeds),
        "recentGames": 0,
        "topGames": 0,
    }
    response = requests.get(EXPLORER_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    for mv in data.get("moves", []):
        if (
            mv.get("uci") == next_move_uci
            and int(mv.get("gameCount", 0)) >= minimum_games
        ):
            return True
    return False
