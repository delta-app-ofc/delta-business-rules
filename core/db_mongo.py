"""Acesso ao MongoDB do Projeto Delta."""

from __future__ import annotations

from functools import lru_cache

from pymongo import MongoClient

from core.config import MONGODB_URI


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Cliente MongoDB reutilizável. tz_aware para as datas já virem com timezone."""
    return MongoClient(MONGODB_URI, tz_aware=True)
