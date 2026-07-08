# Learn Morse Code — Backend

API REST (Django + Django REST Framework) da plataforma de aprendizado e prática de Código Morse.

## Stack

- Python 3.12+ · Django · Django REST Framework · SimpleJWT
- PostgreSQL · Redis
- [uv](https://docs.astral.sh/uv/) (dependências) · Docker · GitHub Actions

## Setup local

1. Copie as variáveis de ambiente e ajuste (gere uma `SECRET_KEY` real):

   ```sh
   cp .env.example .env
   ```

2. Suba PostgreSQL e Redis:

   ```sh
   docker compose up -d db redis
   ```

3. Instale as dependências e rode as migrações:

   ```sh
   uv sync
   uv run python manage.py migrate
   ```

4. Inicie o servidor:

   ```sh
   uv run python manage.py runserver
   ```

   Verificação rápida: `GET http://localhost:8000/api/health/` → `{"status": "ok"}`.

Alternativa: subir tudo via Docker com `docker compose up --build`.

## Qualidade e testes

```sh
uv run ruff check .          # lint
uv run ruff format .         # formatação
uv run mypy .                # type checking
uv run pytest                # testes
```

O CI (GitHub Actions) executa lint → type check → testes a cada push/PR.

## Estrutura

```
config/          # settings, urls, wsgi/asgi
apps/
├── accounts/    # usuários e autenticação (Fase 1)
├── morse/       # configurações de Morse e caracteres (Fases 2–3)
├── lessons/     # lições (Fase 3)
├── practice/    # registro de treino (Fase 4)
└── statistics/  # estatísticas agregadas (Fase 5)
```

Requisitos e plano de desenvolvimento: ver `CLAUDE.md`.
