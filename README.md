# techcar-core

Biblioteca compartilhada com os **models** (SQLAlchemy) e as **migrations** (Alembic) do banco de dados do Techcar. Não é uma API: não tem servidor, não expõe rotas HTTP. Outros serviços (como o `techcar-auth-api`) instalam este repositório como dependência para usar os models e garantir que todos falem do mesmo schema de banco.

**Stack:** SQLAlchemy 2.0 · Alembic · PostgreSQL · psycopg

---

## Pré-requisitos

Instale uma vez por máquina:

| Ferramenta                                                        | Para que serve                                           |
| ----------------------------------------------------------------- | -------------------------------------------------------- |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Sobe um PostgreSQL local para rodar/testar as migrations |
| [Git](https://git-scm.com/)                                       | Controle de versão                                       |
| [uv](https://docs.astral.sh/uv/)                                  | Gerencia Python, ambiente virtual e dependências         |

Não é necessário instalar Python separadamente. O `uv` baixa a versão correta (definida em `.python-version`).

### Windows (PowerShell)

```powershell
winget install Docker.DockerDesktop
winget install Git.Git
winget install astral-sh.uv
```

Feche e abra o terminal depois de instalar, e abra o **Docker Desktop** (ele precisa estar rodando).

### macOS

```bash
brew install --cask docker
brew install git uv
```

### Linux

- **Docker:** siga a [documentação oficial](https://docs.docker.com/engine/install/).
- **Git:** `sudo apt install git` (ou equivalente da distro).
- **uv:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Conferindo a instalação

```bash
docker --version
git --version
uv --version
```

---

## Começando

```bash
git clone <url-do-repositorio>
cd techcar-core
cp .env.example .env        # no Windows: Copy-Item .env.example .env
uv sync
```

O `uv sync`:

- Instala todas as dependências (SQLAlchemy, Alembic, psycopg, python-dotenv...)
- Instala o próprio `techcar_core` em modo editável, para que outros comandos (como o Alembic) consigam importar `from techcar_core.models import ...`

**Importante:** este repositório é uma biblioteca. Ele não roda sozinho, então não existe um `uv run uvicorn` aqui. O que você normalmente vai fazer é:

1. Rodar as migrations neste repositório (para manter o schema atualizado)
2. Usar este pacote como dependência em outro serviço (ex.: `techcar-auth-api`)

### Sobre o `.env`

O `DATABASE_URL` do `.env.example` já aponta para o Postgres deste repositório (veja abaixo), na **porta 5433**:

```
DATABASE_URL=postgresql+psycopg://app:app@localhost:5433/auth
```

A variável é carregada automaticamente pelo `alembic/env.py` via `python-dotenv` (`load_dotenv()`), então basta o arquivo `.env` existir na raiz — não é preciso exportar a variável manualmente no terminal.

**Se o time definir um Postgres único compartilhado entre serviços** (em vez de um Postgres por repositório), troque o valor do `.env` para apontar para esse banco compartilhado e ignore o `docker-compose.yml` deste repositório. Confirme com o time qual é o caso antes de rodar as migrations em um ambiente que não seja o seu local.

---

## Subindo o PostgreSQL local

Este repositório tem um `docker-compose.yml` com um PostgreSQL só para desenvolvimento/testes de migration.

```bash
docker compose up -d --wait
```

**Por que a porta 5433, e não a 5432 padrão:** o `techcar-auth-api` também sobe um Postgres local, na porta 5432. Usando 5433 aqui, dá para rodar os dois projetos ao mesmo tempo na mesma máquina sem conflito de porta. Se você só usa um dos dois projetos por vez, isso não afeta nada.

Para derrubar o banco (mantendo os dados):

```bash
docker compose down
```

Para derrubar e apagar todos os dados (recomeçar do zero):

```bash
docker compose down -v
```

---

## Rodando as migrations localmente

Com o banco no ar (passo anterior), aplique as migrations existentes:

```bash
uv run alembic upgrade head
```

Confira se as tabelas foram criadas (opcional, via `psql`, DBeaver, TablePlus etc.), apontando para `localhost:5433`, banco `auth`, usuário/senha `app`/`app`.

---

## Criando uma nova migration

Depois de criar ou alterar um model em `src/techcar_core/models/`:

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"
```

1. **Sempre revise o arquivo gerado** em `alembic/versions/`, o autogenerate não é infalível (pode não detectar renomeações, por exemplo).
2. Aplique localmente para confirmar que funciona: `uv run alembic upgrade head`
3. Rode os testes: `uv run pytest`
4. Faça o commit da migration junto com a mudança no model, no mesmo PR

---

## Usando este pacote em outro serviço

Em outro repositório (ex.: `techcar-auth-api`):

```bash
uv add git+https://github.com/sua-org/techcar-core@v0.1.0
```

Sempre referencie uma **tag de versão** (`@v0.1.0`), nunca a branch principal direto, para o outro serviço não quebrar quando este repositório mudar.

No código do serviço:

```python
from techcar_core.models import Tenant, User, Membership, Role
from techcar_core.database import get_session_factory

SessionLocal = get_session_factory(settings.database_url)
```

---

## Publicando uma nova versão

Depois de mergear mudanças na branch principal:

```bash
git tag v0.2.0
git push origin v0.2.0
```

Os serviços que dependem deste pacote só recebem a mudança quando atualizarem explicitamente a tag no próprio `uv add`.

---

## Estrutura do projeto

```
techcar-core/
├── src/techcar_core/
│   ├── database.py       # Base declarativa, engine, sessão
│   └── models/            # Tenant, User, Role, Membership...
├── alembic/
│   ├── env.py              # carrega o .env e aponta para Base.metadata
│   └── versions/           # histórico de migrations
├── tests/
├── docker-compose.yml      # PostgreSQL local (porta 5433)
├── .env.example
├── alembic.ini
└── pyproject.toml
```

---

## Comandos úteis

| Comando                                           | O que faz                                        |
| ------------------------------------------------- | ------------------------------------------------ |
| `uv sync`                                         | Instala dependências e o pacote em modo editável |
| `docker compose up -d --wait`                     | Sobe o PostgreSQL local (porta 5433)             |
| `docker compose down`                             | Derruba o Postgres, mantendo os dados            |
| `docker compose down -v`                          | Derruba o Postgres e apaga os dados              |
| `uv run alembic upgrade head`                     | Aplica as migrations pendentes                   |
| `uv run alembic revision --autogenerate -m "..."` | Gera uma nova migration                          |
| `uv run alembic downgrade -1`                     | Desfaz a última migration                        |
| `uv run pytest`                                   | Roda os testes                                   |
| `uv run ruff check .`                             | Roda o linter                                    |
| `uv run mypy src`                                 | Checagem de tipos                                |

---

## Problemas comuns

**`ModuleNotFoundError: No module named 'techcar_core'`**
O pacote não foi instalado em modo editável. Rode `uv sync` na raiz do projeto. Confirme também que o `pyproject.toml` tem a seção `[build-system]` com o Hatchling configurado.

**`error during connect` / `Cannot connect to the Docker daemon`**
O Docker Desktop não está aberto. Abra-o e rode o comando de novo.

**`KeyError: 'DATABASE_URL'` ao rodar o Alembic**
Falta o arquivo `.env` na raiz do projeto, ou ele não tem a variável `DATABASE_URL`. Confirme que copiou o `.env.example` para `.env` (`uv sync` não faz isso sozinho). Se o erro persistir, confira que `python-dotenv` está instalado (`uv sync` de novo) e que a linha `load_dotenv()` está no topo do `alembic/env.py`.

**Porta 5433 já em uso**
Outro processo já está usando essa porta na sua máquina. Pare o processo, ou troque a porta no `docker-compose.yml` (dos dois lados do `"5433:5432"`) e atualize o `.env` de acordo.

**A migration `autogenerate` veio vazia ou incompleta**
Confirme que todos os models estão importados em `src/techcar_core/models/__init__.py`. O Alembic só detecta tabelas de classes que foram efetivamente importadas em algum ponto do código.

---

## Contribuindo

- Rode `uv run ruff check .` e `uv run mypy src` antes de abrir um PR.
- Toda mudança em um model precisa vir acompanhada da migration correspondente.
- Depois do merge, publique uma nova tag de versão (veja "Publicando uma nova versão") e avise os times que dependem deste pacote.
