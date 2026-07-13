FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Instala dependências antes de copiar o código para aproveitar o cache de camadas.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# collectstatic no build (WhiteNoise serve em runtime). O settings exige
# SECRET_KEY e DATABASE_URL para carregar — valores dummy só para este passo;
# nenhuma conexão é aberta e nada disso fica na imagem final.
RUN SECRET_KEY=build-only-collectstatic \
    DATABASE_URL=postgres://build:build@localhost:5432/build \
    python manage.py collectstatic --noinput

EXPOSE 8000

# `migrate` no start porque o free tier do Render não tem pre-deploy command;
# as data migrations semeiam lições/caracteres. O Render injeta a porta em $PORT.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi -b 0.0.0.0:${PORT:-8000} --workers 2"]
