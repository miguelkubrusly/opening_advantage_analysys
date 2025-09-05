from __future__ import annotations

from typing import Any, Iterable
import json

from SDK.create_request import create_request
from SDK.utils import get_lichess_token
from SDK.sdk_types import NdjsonGame, DownloadParams


def download_games(
    username: str,
    *,
    # Windowing and sizing
    max: int | None = None,
    since: int | None = None,  # epoch ms
    until: int | None = None,  # epoch ms
    # Filters
    rated: bool | None = None,
    perf_type: str | None = None,  # bullet|blitz|rapid|classical|ultraBullet|correspondence|...
    color: str | None = None,  # white|black
    vs: str | None = None,  # opponent username
    analysed: bool | None = None,
    ongoing: bool | None = None,
    finished: bool | None = None,
    sort: str | None = None,  # dateDesc|dateAsc
    # Toggles for fields
    moves: bool | None = None,
    tags: bool | None = None,
    clocks: bool | None = None,
    evals: bool | None = None,
    opening: bool | None = None,
    accuracy: bool | None = None,  # requires analysed=True
    last_fen: bool | None = None,  # NDJSON only
    # Output
    format: str = "ndjson",  # "ndjson" (recommended) or "pgn"
    token: str | None = None,  # Lichess API token (optional for public)
    timeout: tuple[float | int, float | int] = (5, 30),
) -> list[NdjsonGame] | str:
    """Download games of a Lichess user.

    - Default returns NDJSON parsed into a list of dicts (recommended for processing).
    - Set format="pgn" to get a PGN string.
    - When requesting accuracy, ensure analysed=True.
    """
    if not username:
        raise ValueError("username is required")

    fmt = format.lower()
    if fmt not in {"ndjson", "pgn"}:
        raise ValueError("format must be 'ndjson' or 'pgn'")

    # Build query params using API's expected casing
    params: DownloadParams = {}
    param_mappings = {
        "max": max,
        "since": since,
        "until": until,
        "rated": rated,
        "perfType": perf_type,
        "color": color,
        "vs": vs,
        "analysed": analysed,
        "ongoing": ongoing,
        "finished": finished,
        "sort": sort,
        "moves": moves,
        "tags": tags,
        "clocks": clocks,
        "evals": evals,
        "opening": opening,
        "accuracy": accuracy,
        "lastFen": last_fen
    }

    for key, value in param_mappings.items():
        if value is not None:
            if key in ["rated", "analysed", "ongoing", "finished", "moves", "tags",
                       "clocks", "evals", "opening", "accuracy", "lastFen"]:
                params[key] = bool(value)
            elif key in ["max", "since", "until"]:
                params[key] = int(value)
            else:
                params[key] = value
```

    if accuracy and not analysed:
        # Warn early to prevent surprising empty accuracy fields
        # (API permits the call but will not include accuracy without analysed=true)
        raise ValueError("accuracy=True requires analysed=True")

    url = f"https://lichess.org/api/games/user/{username}"
    accept = "application/x-ndjson" if fmt == "ndjson" else "application/x-chess-pgn"

    bearer = token or get_lichess_token()

    resp = create_request(
        url,
        method="GET",
        accept=accept,
        api_key=bearer,
        use_bearer=True,
        params=params,  # type: ignore[arg-type]
        timeout=timeout,
        stream=True,
    )

    if resp is None:
        raise RuntimeError("Request failed or no response returned")

    # Raise explicit error for non-2xx
    try:
        resp.raise_for_status()
    except Exception as e:
        body = None
        try:
            body = resp.text[:500]
        except Exception:
            pass
        raise RuntimeError(f"HTTP {resp.status_code}: {e}. Body: {body}")

    if fmt == "pgn":
        return resp.text

    # NDJSON: parse each line to JSON object
    games: list[NdjsonGame] = []
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        line = line.strip()
        if not line:
            continue
        obj: NdjsonGame = json.loads(line)
        games.append(obj)
    return games
