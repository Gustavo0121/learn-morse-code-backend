<div align="center">

# Learn Morse Code — API

Backend Django do Learn Morse Code — API REST que sustenta a plataforma de aprendizado e prática de código Morse.

<br>

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-A30000?style=for-the-badge)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-FF4438?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![uv](https://img.shields.io/badge/uv-DE5FE9?style=for-the-badge&logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com/)

</div>

## Sobre

API REST em Django + Django REST Framework que fornece autenticação, conteúdo educacional, registro de treinos e estatísticas para o [frontend Angular](https://github.com/Gustavo0121/learn-morse-code-frontend). A geração de áudio Morse acontece inteiramente no navegador — o backend cuida dos dados e das regras.

## Funcionalidades

- **Autenticação JWT segura**: access token de vida curta no corpo; refresh token rotacionado em cookie `httpOnly`/`SameSite=Strict`, com blacklist e proteção CSRF.
- **Configurações de treino por usuário**: velocidade (WPM), frequência, volume, tipo de onda e tecla de captura — validadas no servidor, com whitelist de teclas gerenciável pelo admin.
- **Conteúdo educacional**: trilha de lições e o alfabeto Morse completo (padrão ITU-R M.1677-1), populados por data migrations.
- **Registro de prática**: valida e classifica os pressionamentos de tecla no servidor (fórmula PARIS derivada do WPM do usuário) e calcula acertos — o cliente nunca decide o que está `correct`.
- **Estatísticas agregadas**: precisão, velocidade média e tempo de treino recalculados a cada tentativa.
- **Hardening**: rate limiting por IP/usuário (Redis), CORS explícito, CSP e headers de segurança, `pip-audit` no CI.
- **Documentação interativa**: Swagger UI em `/api/docs` e schema OpenAPI 3 em `/api/schema`.

## Rodando localmente

```sh
cp .env.example .env             # ajuste (gere uma SECRET_KEY real)
docker compose up -d db redis    # PostgreSQL e Redis
uv sync                          # dependências
uv run python manage.py migrate  # migrações + seeds (lições, caracteres)
uv run python manage.py runserver
```

Verificação rápida: `GET http://localhost:8000/api/health/` → `{"status": "ok"}`. Alternativa: subir tudo via Docker com `docker compose up --build`.

## Comandos

| Comando                  | Descrição                                       |
| ------------------------ | ----------------------------------------------- |
| `uv run pytest`          | Testes                                          |
| `uv run pytest --cov`    | Testes com cobertura (meta: ≥ 80%, gate no CI)  |
| `uv run ruff check .`    | Lint (inclui regras de segurança do bandit)     |
| `uv run ruff format .`   | Formatação                                      |
| `uv run mypy .`          | Type checking                                   |

## Documentação

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura, endpoints e contratos da API, segurança, qualidade e CI/CD.
- **`/api/docs`** — Swagger UI gerado do código (drf-spectacular), sempre em dia com a API real.

## Frontend

A interface é o [learn-morse-code-frontend](https://github.com/Gustavo0121/learn-morse-code-frontend) (Angular). O CI valida lint, testes, auditoria de segurança e build Docker a cada push; push na `main` publica a imagem no GHCR e dispara o deploy no Render.

## Bugs e sugestões

Encontrou um bug ou tem uma ideia? Abra uma [issue](https://github.com/Gustavo0121/learn-morse-code-backend/issues) — o [`CONTRIBUTING.md`](CONTRIBUTING.md) descreve o que incluir no reporte.

## Quer contribuir?

Contribuições são bem-vindas! Leia o [`CONTRIBUTING.md`](CONTRIBUTING.md) para preparar o ambiente, entender o fluxo de branches e o que esperamos do código.

## Código de conduta

Ao participar do projeto, você concorda com o nosso [Código de Conduta](CODE_OF_CONDUCT.md).

## Segurança

Vulnerabilidades não devem ser reportadas em issues públicas — veja o processo de divulgação responsável em [`SECURITY.md`](SECURITY.md).

## Licença

Distribuído sob a licença [Apache 2.0](LICENSE).
