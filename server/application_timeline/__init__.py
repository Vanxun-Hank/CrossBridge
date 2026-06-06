"""Function 3 — CrossBridge application-timeline service (port 8083).

Independent FastAPI service that turns a completed Function 2 document package
into a loan-application progress timeline. The SME submits an application once
materials are ready; the bank advances six fixed nodes from a hidden admin
backend; the SME watches progress update live over SSE.

Fully decoupled from Functions 1 and 2: its own SQLite database, its own Alembic
environment, and a synthetic demo identity (``demo_sme_001``). It never writes to
another service's database; submission-readiness is delegated to Function 2 (the
single source of truth) over HTTP.
"""
