from typing import Union
from pathlib import Path
from datetime import datetime, timedelta, timezone

StrOrPath = Union[str, Path]

def now() -> datetime:
    JST = timezone(timedelta(hours=9))
    return datetime.now(JST)

def timedelta2HMS(total_sec:int) -> str:
    h = total_sec // 3600
    m = total_sec % 3600 // 60
    s = total_sec % 60
    return f'{h:3d}h {m:2d}m {s:2d}s'
