"""Isolated PostgreSQL database helpers for the G2 regression scripts."""

from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import psycopg
from dotenv import dotenv_values
from psycopg import sql


ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def temporary_database(config_path):
    config = dotenv_values(config_path, interpolate=False)
    settings = {
        key[2:].lower(): config[key]
        for key in ("PGHOST", "PGPORT", "PGUSER", "PGPASSWORD") if config.get(key)
    }
    name = "tv3_g2_check_" + uuid4().hex[:12]
    with psycopg.connect(dbname="postgres", autocommit=True, connect_timeout=5, **settings) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        try:
            with psycopg.connect(dbname=name, autocommit=True, connect_timeout=5, **settings) as conn:
                yield conn
        finally:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
