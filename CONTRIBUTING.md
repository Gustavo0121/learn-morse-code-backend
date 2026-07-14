# Contribuindo

Obrigado pelo interesse em contribuir com o Learn Morse Code! Este guia explica como preparar o ambiente e o que esperamos de uma contribuição.

## Antes de começar

- Procure nas [issues](https://github.com/Gustavo0121/learn-morse-code-backend/issues) se o bug/ideia já foi reportado.
- Para mudanças grandes, abra uma issue primeiro para alinharmos a abordagem antes de você investir tempo no código.
- Leia o [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — ele documenta as decisões técnicas e os contratos da API que as contribuições devem respeitar.

## Preparando o ambiente

1. Faça um fork e clone o repositório.
2. Instale o [uv](https://docs.astral.sh/uv/) e use **Python 3.12+**.
3. Configure e suba o ambiente:

   ```sh
   cp .env.example .env             # ajuste (gere uma SECRET_KEY real)
   docker compose up -d db redis
   uv sync
   uv run python manage.py migrate
   uv run python manage.py runserver
   ```

4. Confirme que está tudo de pé: `GET http://localhost:8000/api/health/` → `{"status": "ok"}`.

## Fluxo de trabalho

- Crie sua branch a partir da **`dev`** e abra o PR **para `dev`** (a `main` é reservada para releases — push nela publica em produção).
- Antes de abrir o PR, rode localmente o mesmo pipeline do CI:

  ```sh
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy .
  uv run pytest --cov
  ```

- O CI precisa passar por completo para o PR ser considerado (inclui system checks do Django, verificação de migrações faltantes, `pip-audit` e build Docker).

## O que esperamos do código

- **Testes acompanham a mudança** (pytest + pytest-django, em `apps/<app>/tests/`). A cobertura do projeto deve se manter **≥ 80%** (gate no CI).
- **Validação sempre no servidor**: limites, choices e whitelists vivem em serializers/models — nunca assuma que o frontend validou.
- **Migrações**: nunca edite uma migração já aplicada; conteúdo educacional (lições, caracteres, teclas permitidas) entra por data migration ou Django admin.
- **ORM sempre** — nada de SQL cru interpolado.
- **Contratos da API são estáveis**: nomes de campo, formato do cookie de refresh e o header `X-CSRF-Protection` são espelhados pelo frontend; mudanças de contrato precisam ser coordenadas nos dois repositórios.
- **Secrets só em variáveis de ambiente** (`.env` local, fora do git). Nunca logue tokens ou senhas.
- Estilo: `ruff check` (inclui regras de segurança do bandit) e `ruff format` sem pendências; `mypy` limpo.

## Reportando bugs e sugerindo funcionalidades

Abra uma [issue](https://github.com/Gustavo0121/learn-morse-code-backend/issues) descrevendo:

- **Bug**: passos para reproduzir (requisição/payload), comportamento esperado × observado, versão/commit.
- **Funcionalidade**: o problema que ela resolve e, se possível, uma proposta de contrato (endpoint, corpo, resposta).

Vulnerabilidades de segurança **não** devem ser abertas como issue pública — veja [`SECURITY.md`](SECURITY.md).
