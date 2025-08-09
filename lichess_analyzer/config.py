from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
import os


def _load_env() -> None:
    # 1) tenta no CWD (bom para rodar via CLI/heredoc)
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path)
        return
    # 2) fallback: raiz do projeto (2 níveis acima deste arquivo)
    project_root = Path(__file__).resolve().parents[1]
    candidate = project_root / ".env"
    if candidate.exists():
        load_dotenv(candidate)


class AnalyzerSettings(BaseModel):
    theory_minimum_games: int = 20
    opening_explorer_speeds: list[str] = ["bullet", "blitz", "rapid"]
    advantage_expected_centipawns: int = 80
    turnaround_swing_centipawns: int = 150
    moves_to_scan_after_opponent_novelty: int = 12
    cloud_evaluation_multi_pv: int = 1
    polite_delay_seconds_between_cloud_calls: float = 0.4


def load_settings() -> AnalyzerSettings:
    _load_env()
    return AnalyzerSettings()


def get_lichess_api_token() -> str | None:
    _load_env()
    return os.getenv("LICHESS_API_TOKEN") or os.getenv("LICHESS_TOKEN")
