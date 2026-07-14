# Política de Segurança

## Versões suportadas

Este projeto entrega continuamente a partir da branch `main` — apenas a versão em produção (último deploy da `main`) recebe correções de segurança.

## Reportando uma vulnerabilidade

**Não abra issue pública para vulnerabilidades.**

Prefira o canal privado do GitHub: na aba **Security** do repositório, use **"Report a vulnerability"** (GitHub Private Vulnerability Reporting). Alternativamente, envie e-mail para **gus0512san@gmail.com** com o assunto `[SECURITY] learn-morse-code`.

Inclua no reporte:

- Descrição da vulnerabilidade e o impacto potencial.
- Passos para reproduzir (endpoint, requisição/payload, configuração necessária).
- Versão/commit afetado e ambiente, se relevante.

Você receberá uma confirmação de recebimento em até **72 horas** e atualizações conforme a análise avançar. Pedimos que a divulgação pública aguarde a correção estar em produção (divulgação coordenada).

## Escopo

- Este repositório cobre a **API** (Django + DRF). Vulnerabilidades na interface devem ser reportadas no repositório do [frontend](https://github.com/Gustavo0121/learn-morse-code-frontend) pelo mesmo processo.
- Contexto útil: autenticação JWT com refresh token em cookie `httpOnly` rotacionado, rate limiting por IP/usuário e validação de toda entrada no servidor — detalhes nas seções de autenticação e segurança do [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Dependências passam por `pip-audit` no CI e o lint inclui as regras de segurança do bandit; reportes sobre advisories em dependências são bem-vindos, especialmente quando exploráveis no contexto da API.
