"""Utility to parse PGN formatted games.

The original implementation relied on :mod:`python-chess`'s PGN parser. For
the purposes of these exercises we want to avoid that dependency while still
providing a reasonably capable parser. The previous implementation also only
returned the first game found in a PGN string, silently discarding additional
games contained in the same text. This bug meant that when a single PGN string
contained multiple games only the first one would ever be analysed.

This module now includes a very small PGN reader that extracts the headers and
move text for **all** games contained in each supplied PGN string.
"""

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass
class PGNGame:
    """Minimal representation of a PGN game.

    Only the game headers and raw move text are stored which is sufficient for
    our analysis and testing needs.
    """

    headers: dict[str, str]
    moves: str


_HEADER_RE = re.compile(r"\[(\w+)\s+\"([^\"]*)\"\]")


def _split_pgn_text(text: str) -> list[str]:
    """Split a PGN text into individual game chunks."""

    # Games are separated by a blank line followed by a new header section
    return [chunk for chunk in re.split(r"\n\s*\n(?=\[)", text.strip()) if chunk.strip()]


def parse_pgn_games(pgn_texts: Iterable[str]) -> list[PGNGame]:
    """Parse one or more PGN strings into :class:`PGNGame` objects.

    The previous implementation only read the first game from each string.
    The new logic iterates over all games contained in the text ensuring no
    game is skipped.
    """

    games: list[PGNGame] = []
    for text in pgn_texts:
        for chunk in _split_pgn_text(text):
            headers = dict(_HEADER_RE.findall(chunk))
            parts = chunk.split("\n\n", 1)
            moves = parts[1].strip() if len(parts) > 1 else ""
            if headers or moves:
                games.append(PGNGame(headers=headers, moves=moves))
    return games
