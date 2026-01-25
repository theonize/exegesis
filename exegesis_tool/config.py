"""Configuration management for exegesis tool."""

import os
import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Config:
    """Configuration for exegesis tool."""

    # API Settings
    model: str = "claude-opus-4-5-20251101"
    max_tokens: int = 4096

    # Rate Limiting
    max_concurrent_requests: int = 5
    max_retries: int = 3
    base_retry_delay: float = 1.0

    # Database
    db_path: str = "exegesis.db"

    # Output
    content_dir: str = "content"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # or "text"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            model=os.getenv("EXEGESIS_MODEL", cls.model),
            max_tokens=int(os.getenv("EXEGESIS_MAX_TOKENS", cls.max_tokens)),
            max_concurrent_requests=int(os.getenv("EXEGESIS_CONCURRENCY", cls.max_concurrent_requests)),
            max_retries=int(os.getenv("EXEGESIS_MAX_RETRIES", cls.max_retries)),
            db_path=os.getenv("EXEGESIS_DB", cls.db_path),
            content_dir=os.getenv("EXEGESIS_CONTENT_DIR", cls.content_dir),
            log_level=os.getenv("EXEGESIS_LOG_LEVEL", cls.log_level),
            log_format=os.getenv("EXEGESIS_LOG_FORMAT", cls.log_format),
        )


def setup_logging(config: Config) -> logging.Logger:
    """Set up logging based on configuration."""
    logger = logging.getLogger("exegesis")
    logger.setLevel(getattr(logging, config.log_level.upper()))

    handler = logging.StreamHandler()

    if config.log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    logger.addHandler(handler)
    return logger


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add any extra fields
        if hasattr(record, "passage_id"):
            log_entry["passage_id"] = record.passage_id
        if hasattr(record, "perspective"):
            log_entry["perspective"] = record.perspective
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "tokens"):
            log_entry["tokens"] = record.tokens

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)
