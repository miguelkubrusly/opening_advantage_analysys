import os
import sys

# Allow importing the package from the repository root when tests are executed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lichess_analyzer.parsers.pgn_reader import parse_pgn_games


def test_parse_multiple_games_from_single_text():
    pgn = (
        """[Event "Game1"]
1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *

[Event "Game2"]
1. d4 d5 2. c4 e6 3. Nc3 *"""
    )

    games = parse_pgn_games([pgn])

    assert len(games) == 2
    assert games[0].headers["Event"] == "Game1"
    assert games[1].headers["Event"] == "Game2"

