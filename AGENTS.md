# Guia para agentes — Learn Morse Code Backend

API REST (Django + DRF) da plataforma de aprendizado de código Morse. O cliente é uma SPA Angular em repositório separado ([learn-morse-code-frontend](https://github.com/Gustavo0121/learn-morse-code-frontend)).

**Fontes de verdade**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (decisões técnicas, contratos da API e segurança — leia antes de mexer em auth, prática ou validações) e [`CONTRIBUTING.md`](CONTRIBUTING.md) (fluxo de contribuição). Documentação interativa da API em `/api/docs` (Swagger UI).

## Comandos

Tudo roda via [uv](https://docs.astral.sh/uv/) — nunca chame `pip`/`python` diretamente.

| Comando                                     | Uso                                             |
| ------------------------------------------- | ----------------------------------------------- |
| `docker compose up -d db redis`             | Sobe PostgreSQL e Redis locais                   |
| `uv sync`                                   | Instala dependências (dev incluídas)             |
| `uv run python manage.py migrate`           | Migrações (incluem seeds de lições/caracteres)   |
| `uv run python manage.py runserver`         | Dev server em :8000 (`/api/health/` para checar) |
| `uv run pytest`                             | Testes (`apps/<app>/tests/`)                     |
| `uv run pytest apps/practice`               | Testes de um app específico                      |
| `uv run pytest --cov`                       | Cobertura — o CI exige ≥ 80%                     |
| `uv run ruff check .` / `uv run ruff format .` | Lint (inclui regras de segurança do bandit) / formatação |
| `uv run mypy .`                             | Type checking (django-stubs)                     |

## Stack e estrutura

Python 3.12+, Django 5, DRF + SimpleJWT, PostgreSQL (psycopg 3), Redis (cache/throttle), drf-spectacular, Gunicorn + WhiteNoise em produção.

```
config/          # settings, urls, wsgi/asgi
apps/
├── accounts/    # usuários, autenticação JWT, cookie de refresh
├── morse/       # UserMorseSettings, AllowedKey, MorseCharacter
├── lessons/     # lições (conteúdo somente leitura, escrita via admin)
├── practice/    # PracticeHistory + classificação/validação de key_capture
└── statistics/  # agregado UserStatistics (recalculado por signal)
```

## Regras do projeto

- **Migrações**: nunca editar migração já aplicada; o CI roda `makemigrations --check`. Conteúdo (lições, caracteres ITU, teclas permitidas) entra por data migration ou Django admin — nunca hardcoded em view/serializer.
- **Testes acompanham qualquer mudança** (pytest + pytest-django em `apps/<app>/tests/`); cobertura deve se manter ≥ 80% (gate no CI). `assert`/senhas fake são permitidos só em arquivos de teste (per-file-ignores do ruff).
- **Toda entrada do cliente é validada em serializer** — limites numéricos, choices e whitelists vivem no servidor; nunca confiar em validação do frontend.
- **ORM sempre** — nada de SQL cru interpolado.
- **Secrets só em variáveis de ambiente** (django-environ, `.env` local fora do git). Nunca logar tokens.

## Contratos com o frontend (não quebrar)

- Nomes de campo exatos: `speed_wpm` (nunca `speed`); `correct` é sempre calculado no servidor e nunca aceito do cliente.
- `key_capture` pode receber `press_durations` (ms): o servidor reclassifica ponto/traço e deriva `user_answer`. A fórmula (PARIS: ponto = `1200/speed_wpm` ms) vive em `apps/practice/services.py` e é espelhada pelo frontend em `services/morse-timing.ts` — qualquer mudança precisa ser coordenada nos dois repositórios.
- `input_key`/`input_method` são validados contra a tabela `AllowedKey` (whitelist gerenciada pelo admin, exposta em `GET /api/morse-settings/allowed-keys`).
- **Tokens**: access token (15 min) só no corpo da resposta; refresh token (7 dias) só no cookie `refresh_token` (`HttpOnly`, `SameSite=Strict`, `Path=/api/auth`), rotacionado com blacklist. `refresh`/`logout` exigem o header `X-CSRF-Protection: 1` (403 sem ele). Não mudar nomes de cookie/header sem coordenar com o frontend.
- Rate limits atuais: 10/min por IP nas rotas de auth; 60/min anônimo; 120/min autenticado (contadores no Redis).

## Git

- Branches saem da `dev`; PR para `dev`. Push na `main` publica em produção (imagem no GHCR + deploy hook do Render) — nunca commitar direto nela.
- Não faça commit nem push por conta própria: deixe o working tree pronto e resuma as mudanças; o mantenedor commita manualmente.

## Planejamento

Em modo de planejamento, faça perguntas de esclarecimento antes de propor o plano e termine com a lista concisa de dúvidas não resolvidas.
