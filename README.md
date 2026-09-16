# delta-business-rules

Regras de negócio do Projeto Delta que não precisam de IA generativa — cálculos
e processos determinísticos sobre os dados do PostgreSQL/MongoDB, mantidos à
parte do chatbot (`delta-artificial-intelligence`) e do schema
(`delta-sql-database`).

Este README é incremental: cada regra de negócio nova ganha sua própria seção.

---

## Ambiente local de desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps   # espera ficar "healthy"
cp .env.example .env
pip install -r requirements.txt -r requirements-dev.txt
```

Detalhe de origem de cada arquivo de bootstrap (Postgres/Mongo) em
[`db/README.md`](db/README.md).

## Testes

```bash
python -m pytest -q
```

Todos os testes são puros — nenhum depende de Postgres/Mongo rodando.

## Motor de detecção de vazamento (`detection/`)

Migrado do `delta-artificial-intelligence`: calcula `anomaly_detected` em
`consumption_summary` e cria alertas em `alerts_history`, reagindo quase em
tempo real a novas janelas de consumo via MongoDB Change Streams. Não usa
LLM — só regras explicáveis (fluxo contínuo, consumo de madrugada, desvio da
baseline estatística por usuário/hora). Detalhe completo em
[`detection/README.md`](detection/README.md).

O `LeakAgent` do `delta-artificial-intelligence` só lê o que este motor já
calculou — nunca decide um limiar sozinho.

## `core/`

Infra mínima compartilhada pelas regras de negócio: configuração (`.env`),
acesso a PostgreSQL (`core/db_postgres.py`) e MongoDB (`core/db_mongo.py`), e
as estruturas de dados (`core/models.py`). Sem nenhuma lógica de negócio —
só o necessário pra ler/escrever nos bancos do Projeto Delta.
