Delta | Regras de negÃ³cio determinÃ­sticas

![Python](https://img.shields.io/badge/lÃ³gica-Python-3776AB?logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/dados-PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/eventos-MongoDB-47A248?logo=mongodb&logoColor=white)

Este repositÃ³rio reÃºne regras determinÃ­sticas do Delta para cÃ¡lculos e processos de negÃ³cio sobre dados do PostgreSQL e MongoDB. Os mÃ³dulos Python organizam o motor de detecÃ§Ã£o de vazamentos e o acesso compartilhado aos dados.

**Tags:** `#Delta` `#RegrasDeNegÃ³cio` `#Python` `#PostgreSQL` `#MongoDB` `#DeterminÃ­stico`

## SumÃ¡rio

- [VisÃ£o geral](#visÃ£o-geral)
- [Ambiente local](#ambiente-local-de-desenvolvimento)
- [Testes](#testes)
- [DetecÃ§Ã£o de vazamento](#motor-de-detecÃ§Ã£o-de-vazamento-detection)
- [Infraestrutura compartilhada](#core)

## VisÃ£o geral

| Finalidade | Calcular indicadores de consumo e processar alertas com regras determinÃ­sticas. |
| Componentes | Motor de detecÃ§Ã£o de vazamentos em `detection/` e infraestrutura compartilhada em `core/`. |
| IntegraÃ§Ãµes | Acesso a PostgreSQL e MongoDB; o motor de detecÃ§Ã£o usa MongoDB Change Streams. |
| Testes | SuÃ­te pytest para as regras e componentes do repositÃ³rio. |

## Ambiente local de desenvolvimento

Consulte [DOCKER-HELP.md](DOCKER-HELP.md) para usar o ambiente Docker local.

## Testes

```bash
python -m pytest -q
```


## Motor de detecÃ§Ã£o de vazamento (`detection/`)

O motor calcula `anomaly_detected` em `consumption_summary` e cria alertas em `alerts_history` quando recebe novas janelas de consumo por MongoDB Change Streams. Usa regras explicÃ¡veis baseadas em fluxo contÃ­nuo, consumo de madrugada e desvios da baseline estatÃ­stica por usuÃ¡rio e hora. Detalhes em [`detection/README.md`](detection/README.md).

O `LeakAgent` de `delta-artificial-intelligence` consome os alertas calculados por este motor.

## `core/`

O mÃ³dulo `core/` reÃºne a configuraÃ§Ã£o (`.env`), conexÃµes com PostgreSQL (`core/db_postgres.py`) e MongoDB (`core/db_mongo.py`), alÃ©m das estruturas de dados em `core/models.py`.