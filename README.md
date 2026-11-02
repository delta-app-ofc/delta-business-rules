Delta | Regras de negócio determinísticas

![Python](https://img.shields.io/badge/lógica-Python-3776AB?logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/dados-PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/eventos-MongoDB-47A248?logo=mongodb&logoColor=white)

Regras determinísticas do Projeto Delta — cálculos e processos de negócio sobre dados do PostgreSQL e MongoDB, mantidos em um módulo independente do chatbot e dos esquemas de banco.

**Tags:** `#Delta` `#RegrasDeNegócio` `#Python` `#PostgreSQL` `#MongoDB` `#Determinístico`

## Sumário

- [Visão geral](#visão-geral)
- [Ambiente local](#ambiente-local-de-desenvolvimento)
- [Testes](#testes)
- [Detecção de vazamento](#motor-de-detecção-de-vazamento-detection)
- [Infraestrutura compartilhada](#core)

## Visão geral

| Finalidade | Implementar regras de negócio determinísticas sem decisão por IA generativa. |
| Componentes | Motor de detecção de vazamentos em `detection/` e infraestrutura compartilhada em `core/`. |
| Integrações | Acesso a PostgreSQL e MongoDB; o motor de detecção usa MongoDB Change Streams. |
| Testes | O README existente documenta uma suíte pytest pura, sem bancos em execução. |

---

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
