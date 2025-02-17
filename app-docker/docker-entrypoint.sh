#!/bin/bash

alembic -c app/db/migrations/alembic.ini upgrade head
uvicorn "${UVICORN_APP}" --host "${UVICORN_HOST}" --port "${UVICORN_PORT}" --proxy-headers
