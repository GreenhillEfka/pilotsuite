"""Safe logging helpers."""

from __future__ import annotations

import logging
import re


_BEARER = re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+")
_SECRET = re.compile(
    r"(?i)(token|secret|password|api[_-]?key)(\s*[:=]\s*)[^\s,;]+"
)


class RedactingFilter(logging.Filter):
    """Redact common credential shapes before a record is emitted."""

    def filter(self, record: logging.LogRecord) -> bool:
        rendered = record.getMessage()
        rendered = _BEARER.sub(r"\1<redacted>", rendered)
        rendered = _SECRET.sub(r"\1\2<redacted>", rendered)
        record.msg = rendered
        record.args = ()
        return True


def configure_logging(level: str) -> None:
    numeric = logging.DEBUG if level == "trace" else getattr(logging, level.upper())
    handler = logging.StreamHandler()
    handler.addFilter(RedactingFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric)

