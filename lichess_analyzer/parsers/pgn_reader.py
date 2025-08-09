import io
import chess.pgn
from typing import Iterable


def parse_pgn_games(pgn_texts: Iterable[str]) -> list[chess.pgn.Game]:
    games: list[chess.pgn.Game] = []
    for text in pgn_texts:
        game = chess.pgn.read_game(io.StringIO(text))
        if game:
            games.append(game)
    return games
