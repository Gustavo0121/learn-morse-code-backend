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

## API

### Autenticação (Fase 1)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/auth/register` | Cadastro (`username`, `email`, `password`) |
| `POST` | `/api/auth/login` | Retorna o access token no corpo e grava o refresh token em cookie |
| `POST` | `/api/auth/refresh` | Renova o access token a partir do cookie de refresh |
| `POST` | `/api/auth/logout` | Blacklista o refresh token e expira o cookie |
| `GET/PUT` | `/api/users/profile` | Perfil do usuário autenticado (requer `Authorization: Bearer <access>`) |

Como o fluxo de tokens funciona:

- O **access token** (validade de 15 min) é retornado apenas no corpo do login/refresh; o frontend o mantém em memória e o envia via header `Authorization: Bearer`.
- O **refresh token** (validade de 7 dias) nunca aparece no corpo: é entregue no cookie `refresh_token` (`HttpOnly`, `SameSite=Strict`, `Path=/api/auth`, `Secure` fora de DEBUG) e é rotacionado a cada refresh, com blacklist do token anterior.
- **Proteção CSRF**: `refresh` e `logout` dependem do cookie e por isso exigem o header customizado `X-CSRF-Protection: 1`; sem ele a resposta é 403.
- **Rate limiting**: as rotas de autenticação são limitadas a 10 requisições/min por IP (contadores no Redis).

Exemplo:

```sh
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "gu", "password": "sua-senha"}'

curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/auth/refresh \
  -H "X-CSRF-Protection: 1"
```

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
├── accounts/    # usuários e autenticação (Fase 1 ✅)
├── morse/       # configurações de Morse e caracteres (Fases 2–3)
├── lessons/     # lições (Fase 3)
├── practice/    # registro de treino (Fase 4)
└── statistics/  # estatísticas agregadas (Fase 5)
```

Requisitos e plano de desenvolvimento: ver `CLAUDE.md`.
