FROM python:3.13.2-slim-bullseye AS base

ENV APP_NAME  fastapi-template/backend

ENV UVICORN_APP     app.main:app
ENV UVICORN_HOST    0.0.0.0
ENV UVICORN_PORT    8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app-docker/docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT [ "/docker-entrypoint.sh" ]

WORKDIR ${APP_NAME}

FROM base AS deps

RUN apt-get update \
    && apt-get install g++ -y \
    && apt-get install --no-install-recommends -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN python -m pip install --no-cache-dir -U \
    setuptools \
    wheel \
    poetry

COPY ./poetry.lock ./pyproject.toml ./

# Install production dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root --no-interaction --no-ansi

# Development stage
FROM deps AS dev

# Install development dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --with dev --no-root --no-interaction --no-ansi

COPY app ${APP_NAME}

# Prod step
FROM deps AS prod

COPY app ${APP_NAME}/app

WORKDIR ${APP_NAME}

EXPOSE 8000
