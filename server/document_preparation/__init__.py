"""Function 2 — CrossBridge document-preparation service (port 8082).

Independent FastAPI service that helps SMEs assemble cross-border payment and
financing application materials. It is fully decoupled from Function 1: its own
SQLite database, its own Alembic environment, and a read-only material catalog.
It never writes to the Function 1 database.
"""
