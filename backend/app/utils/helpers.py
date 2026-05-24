from datetime import datetime
from typing import Any, Dict
import hashlib
import uuid


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def generate_id() -> str:
    return str(uuid.uuid4())


def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def paginate(items: list, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": items[start:end],
    }


def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
