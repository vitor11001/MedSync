FROM python:3.12-slim-bookworm AS builder
LABEL company="MedSync"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.2

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-ansi --no-interaction


FROM python:3.12-slim-bookworm AS final
LABEL company="MedSync"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=django:django src /app/src
COPY --chown=django:django infra/scripts /app/infra/scripts
COPY --chown=django:django pyproject.toml poetry.lock /app/

RUN chmod -R +x /app/infra/scripts/*.sh \
    && sed -i 's/\r$//' /app/infra/scripts/*.sh

USER django

CMD ["/app/infra/scripts/run-backend.sh"]
