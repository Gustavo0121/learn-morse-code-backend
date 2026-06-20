# Learn Morse Code Backend - Fase 1

Este é o backend da plataforma **Learn Morse Code**, desenvolvido com Python 3.12+, Django e Django REST Framework. A Fase 1 foca na infraestrutura base, gerenciamento de usuários e autenticação JWT.

---

## 🚀 Como Rodar o Projeto

Você pode optar por rodar a aplicação utilizando **Docker** (recomendado para produção/espelhamento) ou **Localmente** (recomendado para desenvolvimento rápido).

### Opção 1: Rodando Localmente (Recomendado)

Esta opção utiliza o `uv` para gerenciar o ambiente de forma rápida e eficiente.

1.  **Instale o `uv`** (caso não tenha):
    *   macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

2.  **Prepare o ambiente:**
    ```bash
    uv sync
    ```

3.  **Configure o Banco de Dados (SQLite):**
    Edite o arquivo `.env` e altere a `DATABASE_URL`:
    ```env
    DATABASE_URL=sqlite:///db.sqlite3
    ```

4.  **Execute as migrações e inicie o servidor:**
    ```bash
    uv run python manage.py migrate
    uv run python manage.py runserver
    ```

---

### Opção 2: Rodando com Docker

Ideal para quem deseja rodar o banco de dados PostgreSQL automaticamente em um container.

1.  **Suba os containers:**
    ```bash
    docker-compose up --build
    ```

2.  **Execute as migrações (em outro terminal):**
    ```bash
    docker-compose exec web uv run python manage.py migrate
    ```

---

## 🛠 Comandos Úteis

*   **Criar Superusuário (Admin):**
    *   Local: `uv run python manage.py createsuperuser`
    *   Docker: `docker-compose exec web uv run python manage.py createsuperuser`

*   **Executar Testes:**
    *   Local: `uv run python manage.py test accounts`
    *   Docker: `docker-compose exec web uv run python manage.py test accounts`

---

## 📖 Documentação da API

Após iniciar o servidor, acesse as documentações interativas:

*   **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
*   **Redoc:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

### Endpoints Principais (Fase 1)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Registro de novo usuário |
| `POST` | `/api/auth/login/` | Login e obtenção de tokens JWT |
| `POST` | `/api/auth/refresh/` | Renovação do Token de Acesso |
| `GET` | `/api/users/profile/` | Visualização do perfil (Requer Auth) |

---

## 🔒 Segurança

*   As credenciais sensíveis estão no arquivo `.env`. **Nunca versione este arquivo em produção.**
*   A autenticação utiliza JWT com expiração de 60 minutos para o token de acesso.
