from dataclasses import dataclass
from typing import Optional, Literal

HitType = Optional[Literal["1B","2B","3B","HR"]]

@dataclass
class EventInfo:
    # event types
    is_batter_event: bool
    is_runner_event: bool

    # batter outcome / core flags
    is_ab: bool
    hit: HitType
    walk: bool
    hbp: bool
    so: bool
    sf: bool
    sh: bool
    fc: bool
    roe: Optional[int]
    dp: bool
    tp: bool

    # pitcher-facing stats
    outs_on_play: int
    errors_on_play: int
    home_run_allowed: bool

    # scoring hints
    explicit_rbis: Optional[int]
    no_rbi: bool

    # parsed details
    field_path: list[int]
    advances: list[tuple[str, str, Optional[str]]]
