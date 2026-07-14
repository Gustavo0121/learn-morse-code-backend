# Arquitetura — Learn Morse Code Backend

Documento técnico de referência: decisões de arquitetura, contratos da API e checklists de segurança/qualidade. Para visão geral e setup, ver o [README](../README.md). A documentação interativa da API (drf-spectacular) fica em **`/api/docs`** (Swagger UI) e **`/api/schema`** (OpenAPI 3) — ambas públicas; os endpoints em si continuam exigindo JWT.

## Stack

- Python 3.12+ · Django 5 · Django REST Framework · SimpleJWT
- PostgreSQL (psycopg 3) · Redis (cache/throttle)
- drf-spectacular (OpenAPI) · Gunicorn + WhiteNoise (produção)
- [uv](https://docs.astral.sh/uv/) (dependências) · Docker · GitHub Actions

## Estrutura

```
config/          # settings, urls, wsgi/asgi
apps/
├── accounts/    # usuários e autenticação
├── morse/       # configurações de Morse, teclas permitidas e caracteres
├── lessons/     # lições
├── practice/    # registro de treino
└── statistics/  # estatísticas agregadas
```

## Autenticação e tokens

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

## Configurações de Morse

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/users/morse-settings` | Configurações de treino do usuário autenticado |
| `PUT` | `/api/users/morse-settings` | Atualiza as configurações |
| `GET` | `/api/morse-settings/allowed-keys` | Whitelist de teclas de captura aceitas |

Corpo/resposta:

```json
{
  "speed_wpm": 20,
  "frequency": 700,
  "volume": 0.8,
  "wave_type": "sine",
  "input_key": "Space"
}
```

Validações no servidor: `speed_wpm` ∈ {5, 10, 15, 20, 30, 40, 60}; `frequency` entre 200 e 2000 Hz; `volume` entre 0.0 e 1.0; `wave_type` ∈ {sine, square, triangle, sawtooth}; `input_key` restrito à tabela `AllowedKey` (dado configurável — teclas são adicionadas/desativadas pelo Django admin, sem deploy; seed inicial: Space, Enter, KeyA, KeyS, KeyD).

As configurações padrão são criadas automaticamente no cadastro do usuário.

## Lições e caracteres Morse

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/lessons` | Lições ordenadas pela posição na trilha (`order`) |
| `GET` | `/api/lessons/{id}` | Detalhe de uma lição (inclui `characters`, o conteúdo da lição) |
| `GET` | `/api/morse-characters` | Alfabeto Morse completo (ITU): 26 letras, 10 números, 18 pontuações |

Conteúdo somente leitura para o aluno — a escrita é restrita ao Django admin. A base é populada por data migrations: 4 lições iniciais (Nível 1 — letras básicas, 2 — números, 3 — palavras, 4 — frases) e os 54 caracteres do padrão ITU-R M.1677-1.

## Prática

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/practice/history` | Registra uma tentativa de exercício |
| `GET` | `/api/practice/history` | Histórico do usuário autenticado (mais recente primeiro) |

Corpo do `POST` (exercício de captura por tecla):

```json
{
  "exercise_type": "key_capture",
  "input_method": "Space",
  "question": "!",
  "expected_answer": "-.-.--",
  "press_durations": [200, 50, 200, 50, 200, 200],
  "response_time": 850
}
```

Como o registro funciona:

- `exercise_type` ∈ {`key_capture`, `multiple_choice`, `listening`}; `input_method` é obrigatório apenas em `key_capture` (validado contra a tabela `AllowedKey`) e proibido nos demais.
- **Captura por toque (mobile)**: `input_method` também aceita o literal `"Touch"` (constante `TOUCH_INPUT_METHOD` em `apps/practice/models.py`) — não é uma tecla, então fica fora da tabela `AllowedKey` para não aparecer no seletor de teclas do Settings.
- Para `key_capture`, o cliente pode enviar `press_durations` (duração de cada pressionamento, em ms): o backend refaz a classificação ponto/traço e deriva `user_answer` no servidor. Cada duração é validada contra um limite dinâmico calculado do `speed_wpm` do usuário (fórmula PARIS: ponto = 1200/WPM ms) — payloads como `999999999` são rejeitados. Sem `press_durations`, `user_answer` é obrigatório no corpo.
- `correct` é sempre calculado no backend comparando `expected_answer` com `user_answer` — nunca aceito do cliente.
- `response_time` (ms) deve estar entre 1 e 300000.

A fórmula de classificação vive em `apps/practice/services.py` e é espelhada pelo frontend (`services/morse-timing.ts`) — mudanças precisam ser coordenadas nos dois repositórios.

## Estatísticas

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/users/statistics` | Desempenho agregado do usuário autenticado |

Resposta:

```json
{
  "characters_seen": 4,
  "characters_correct": 3,
  "accuracy": 0.75,
  "average_speed": 60.0,
  "training_time": 4000,
  "updated_at": "2026-07-11T18:00:00Z"
}
```

- O agregado é recalculado automaticamente a cada tentativa registrada em `/api/practice/history` (signal → `statistics/services.py`); síncrono no MVP, candidato a Redis/Celery no futuro.
- `accuracy` é a fração de acertos (0.0–1.0); `training_time` é a soma dos tempos de resposta em ms; `average_speed` é caracteres por minuto derivada do tempo total de resposta.
- Somente leitura: qualquer escrita do cliente (`POST`/`PUT`/`PATCH`) responde 405. Usuários sem histórico recebem o agregado zerado.

## Segurança

- **Rate limiting global**: 60 req/min por IP para anônimos e 120 req/min por usuário autenticado, além dos 10 req/min por IP nas rotas de autenticação.
- **CORS**: origens explícitas via `CORS_ALLOWED_ORIGINS` (nunca `*`), com credenciais habilitadas para o cookie de refresh e o header `X-CSRF-Protection` liberado no preflight. Em produção, o frontend é servido same-origin (rewrite `/api/*` no host estático), então CORS fica dispensado.
- **Headers**: `Content-Security-Policy` restritiva em todas as respostas, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`.
- **Produção (`DEBUG=False`)**: redirect HTTPS obrigatório, HSTS de 1 ano com subdomínios, cookies `Secure`, API somente JSON (Browsable API desligada). Atrás de proxy TLS, ligar `USE_X_FORWARDED_PROTO`.
- **Dependências**: `pip-audit` roda no CI (job `security`) contra o lockfile completo; o lint inclui as regras de segurança do bandit (`S`) via ruff.

Auditoria manual de dependências:

```sh
uv export --no-emit-project --format requirements-txt -o requirements-audit.txt
uv run pip-audit --disable-pip -r requirements-audit.txt
```

## Qualidade e testes

```sh
uv run ruff check .          # lint (inclui regras de segurança do bandit)
uv run ruff format .         # formatação
uv run mypy .                # type checking
uv run pytest                # testes
uv run pytest --cov          # testes com cobertura (meta: ≥ 80%)
```

O CI também roda os system checks do Django e `makemigrations --check` (migração faltando falha o pipeline).

## CI/CD e deploy

Pipeline (GitHub Actions), a cada push/PR em `dev`/`main`:

```
Lint → Testes (cobertura ≥ 80%) → Security Scan (pip-audit) → Docker Build → Deploy
```

- **Docker Build**: valida o build em PRs; em push nas branches principais também publica a imagem em `ghcr.io/gustavo0121/learn-morse-code-backend` (tags: SHA, branch e `latest` na branch default).
- **Deploy**: em push na `main`, dispara o deploy hook do Render (secret `RENDER_DEPLOY_HOOK_URL`; sem o secret o job apenas avisa — o auto-deploy do Render assume). Para condicionar o deploy ao CI verde, desligue o auto-deploy no painel do Render e cadastre o secret.
- **Migrations** rodam automaticamente no start do container (`migrate --noinput` antes do Gunicorn), incluindo os seeds de lições/caracteres.
- **Rollback**: o dashboard do Render permite voltar para qualquer deploy anterior (aba Deploys → Rollback). Rollback de código não desfaz migração aplicada — prefira migrações aditivas (expand/contract); para reverter uma migração destrutiva, `manage.py migrate <app> <migração_anterior>`.
