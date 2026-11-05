# delta-business-rules

Regras de negócio do Projeto Delta que não precisam de IA generativa — cálculos
e processos determinísticos sobre os dados do PostgreSQL/MongoDB, mantidos à
parte do chatbot (`delta-artificial-intelligence`) e do schema
(`delta-sql-database`).

Este README é incremental: cada regra de negócio nova ganha sua própria seção.

---

## Ambiente local de desenvolvimento

Consulte [DOCKER-HELP.md](DOCKER-HELP.md) para usar o ambiente Docker local.

## Testes

```bash
python -m pytest -q
```

Todos os testes são puros — nenhum depende de Postgres/Mongo rodando.

## Detecção na API Mongo

O detector passa a pertencer ao `delta-api-mongo` (Java), acionado pela gravação
de telemetria, com evidências em `consumption_summary` e `alerts_history`.
Os casos reaproveitáveis do Python estão exportados nas fixtures JSON do detector Java.
O LeakAgent lê os resultados; tarifas permanecem neste repositório em `update_tariffs/`.

Esta remoção deve ser integrada somente após validar o detector Java em produção
com ingestão, baseline e alertas persistidos. A branch de migração não comprova esse cutover.
O procedimento e a ordem entre repositórios ficam no
[delta-handbook](https://github.com/delta-app-ofc/delta-handbook/blob/docs/deteccao-anomalias-ia/IA/deteccao-anomalias.md).

## `core/`

Infra mínima compartilhada pelas regras de negócio: configuração (`.env`),
acesso a PostgreSQL (`core/db_postgres.py`) e MongoDB (`core/db_mongo.py`), e
as estruturas de dados (`core/models.py`). Sem nenhuma lógica de negócio —
só o necessário pra ler/escrever nos bancos do Projeto Delta.
