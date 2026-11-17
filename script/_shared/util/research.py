"""Final paper: research. See core/description.md."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any
import numpy as np


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def arr_hash(a: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest().upper()


def text_hash(lines: list[str]) -> str:
    return sha256_bytes("\n".join(lines).encode("utf-8"))


def safe_path(p: Path) -> Path:
    """이미 존재하는 파일은 덮어쓰지 않고 새 버전 이름을 쓴다."""
    if not p.exists():
        return p
    v = 2
    while True:
        cand = p.parent / f"{p.stem}_v{v}{p.suffix}"
        if not cand.exists():
            return cand
        v += 1


def is_nan(x: Any) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def fnum(x: Any, nd: int = 4) -> str:
    return "N/A" if is_nan(x) else f"{x:.{nd}f}"


def fpct(x: Any, nd: int = 2) -> str:
    return "N/A" if is_nan(x) else f"{x:+.{nd}f}%"


def fratio(num: int, den: int) -> str:
    return "정의 불가" if den == 0 else f"{100 * num / den:.1f}% ({num}/{den})"


def improvement(baseline: float, model: float) -> float:
    if is_nan(baseline) or is_nan(model) or baseline == 0:
        return float("nan")
    return 100.0 * (baseline - model) / baseline


def verdict_word(x: Any) -> str:
    if is_nan(x):
        return "N/A"
    return "오차 감소" if x > 0 else "오차 증가" if x < 0 else "동일"
