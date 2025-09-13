from __future__ import annotations
from typing import Optional, Dict, Any, List, Tuple
from .models import EventInfo

BATTER_VERBS: Dict[str, Dict[str, Any]] = {
    "1B": {"is_ab": True,  "hit": "1B"},
    "2B": {"is_ab": True,  "hit": "2B"},
    "3B": {"is_ab": True,  "hit": "3B"},
    "HR": {"is_ab": True,  "hit": "HR"},
    "BB": {"is_ab": False, "walk": True},
    "IBB":{"is_ab": False, "walk": True},
    "HBP":{"is_ab": False, "hbp": True},
    "K":  {"is_ab": True,  "so": True},
    "CI": {"is_ab": False},
    "G":  {"is_ab": True},
    "F":  {"is_ab": True},
    "L":  {"is_ab": True},
    "FC": {"is_ab": True, "fc": True},
    "E":  {"is_ab": True},
    "DP": {"is_ab": True, "dp": True},
    "TP": {"is_ab": True, "tp": True},
    "SF": {"is_ab": False, "sf": True},
    "SH": {"is_ab": False, "sh": True},
}

RUNNER_VERBS: Dict[str, Dict[str, Any]] = {
    "SB": {},
    "CS": {},
    "PO": {},
    "BK": {},
    "WP": {},
    "PB": {},
}

def _mod_rbi(ev: EventInfo, arg: Optional[str]):
    ev.explicit_rbis = int(arg) if arg else (ev.explicit_rbis or 1)

def _mod_norbi(ev: EventInfo, arg: Optional[str]):
    ev.no_rbi = True

def _mod_roe(ev: EventInfo, arg: Optional[str]):
    ev.errors_on_play += 1
    if arg and arg.isdigit():
        ev.roe = int(arg)

def _mod_sf(ev: EventInfo, arg: Optional[str]):
    ev.sf = True
    ev.is_ab = False

def _mod_sh(ev: EventInfo, arg: Optional[str]):
    ev.sh = True
    ev.is_ab = False

MODIFIERS = {
    "RBI":  _mod_rbi,
    "NoRBI":_mod_norbi,
    "ROE":  _mod_roe,
    "SF":   _mod_sf,
    "SH":   _mod_sh,
}

def parse_field_path(token: str) -> List[int]:
    if not token:
        return []
    parts = token.split("-")
    out: List[int] = []
    for p in parts:
        if p.isdigit():
            out.append(int(p))
    return out

def parse_advances(s: Optional[str]) -> List[Tuple[str, str, Optional[str]]]:
    if not s:
        return []
    out: List[Tuple[str, str, Optional[str]]] = []
    for seg in s.split(";"):
        seg = seg.strip()
        if not seg:
            continue
        if "(" in seg and seg.endswith(")"):
            main, note = seg[:-1].split("(", 1)
            note = note.strip()
        else:
            main, note = seg, None
        if "-" not in main:
            raise ValueError(f"Invalid advance segment: {seg}")
        from_id, dest = main.split("-", 1)
        out.append((from_id.strip(), dest.strip(), note))
    return out

def tokenize_event(raw: str):
    chunks = raw.split("+")
    head = chunks[0]
    mods  = chunks[1:]
    i = 0
    while i < len(head) and head[i].isalpha():
        i += 1
    verb = head[:i]
    suffix = head[i:]
    return verb, suffix, mods

def classify_event(raw_event: str, advances_str: Optional[str] = None) -> EventInfo:
    verb, suffix, mods = tokenize_event(raw_event)

    is_batter = verb in BATTER_VERBS
    is_runner = verb in RUNNER_VERBS
    if not (is_batter or is_runner):
        raise ValueError(f"Unknown verb: {verb} in event '{raw_event}'")

    ev = EventInfo(
        is_batter_event=is_batter,
        is_runner_event=is_runner,
        is_ab=False, hit=None, walk=False, hbp=False, so=False,
        sf=False, sh=False, fc=False, roe=None, dp=False, tp=False,
        outs_on_play=0, errors_on_play=0, home_run_allowed=False,
        explicit_rbis=None, no_rbi=False,
        field_path=[], advances=parse_advances(advances_str),
    )

    table = BATTER_VERBS if is_batter else RUNNER_VERBS
    for k, v in table.get(verb, {}).items():
        setattr(ev, k, v)

    if verb in ("1B","2B","3B","HR"):
        ev.hit = verb
        ev.is_ab = True
        ev.home_run_allowed = (verb == "HR")

    elif verb == "K":
        ev.so = True
        ev.is_ab = True

    elif verb in ("G","F","L"):
        ev.field_path = parse_field_path(suffix)

    elif verb == "FC":
        ev.fc = True
        ev.field_path = parse_field_path(suffix)

    elif verb == "E":
        if suffix and suffix.isdigit():
            ev.roe = int(suffix)
        ev.errors_on_play += 1

    elif verb in ("DP","TP"):
        ev.field_path = parse_field_path(suffix)

    elif verb in ("SF","SH"):
        ev.field_path = parse_field_path(suffix)

    elif verb in ("SB","CS","PO","BK","WP","PB"):
        pass

    for m in mods:
        if "(" in m and m.endswith(")"):
            name, arg = m[:-1].split("(", 1)
        else:
            name, arg = m, None
        fn = MODIFIERS.get(name)
        if fn:
            fn(ev, arg)

    return ev
