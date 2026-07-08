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

### Configurações de Morse (Fase 2)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/users/morse-settings` | Configurações de treino do usuário autenticado |
| `PUT` | `/api/users/morse-settings` | Atualiza as configurações |

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

### Lições e caracteres Morse (Fase 3)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/lessons` | Lições ordenadas pela posição na trilha (`order`) |
| `GET` | `/api/lessons/{id}` | Detalhe de uma lição |
| `GET` | `/api/morse-characters` | Alfabeto Morse completo (ITU): 26 letras, 10 números, 18 pontuações |

Conteúdo somente leitura para o aluno — a escrita é restrita ao Django admin. A base é populada por data migrations: 4 lições iniciais (Nível 1 — letras básicas, 2 — números, 3 — palavras, 4 — frases) e os 54 caracteres do padrão ITU-R M.1677-1.

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
├── morse/       # configurações de Morse e caracteres (Fases 2–3 ✅)
├── lessons/     # lições (Fase 3 ✅)
├── practice/    # registro de treino (Fase 4)
└── statistics/  # estatísticas agregadas (Fase 5)
```

Requisitos e plano de desenvolvimento: ver `CLAUDE.md`.
