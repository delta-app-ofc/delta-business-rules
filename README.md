Delta | Regras de negócio determinísticas

![Python](https://img.shields.io/badge/lógica-Python-3776AB?logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/dados-PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/eventos-MongoDB-47A248?logo=mongodb&logoColor=white)

Este repositório reúne regras determinísticas do Delta para cálculos e processos de negócio sobre dados do PostgreSQL e MongoDB. Os módulos Python organizam o motor de detecção de vazamentos e o acesso compartilhado aos dados.

**Tags:** `#Delta` `#RegrasDeNegócio` `#Python` `#PostgreSQL` `#MongoDB` `#Determinístico`

## Sumário

- [Visão geral](#visão-geral)
- [Ambiente local](#ambiente-local-de-desenvolvimento)
- [Testes](#testes)
- [Detecção de vazamento](#motor-de-detecção-de-vazamento-detection)
- [Infraestrutura compartilhada](#core)

## Visão geral

| Finalidade | Calcular indicadores de consumo e processar alertas com regras determinísticas. |
| Componentes | Motor de detecção de vazamentos em `detection/` e infraestrutura compartilhada em `core/`. |
| Integrações | Acesso a PostgreSQL e MongoDB; o motor de detecção usa MongoDB Change Streams. |
| Testes | Suíte pytest para as regras e componentes do repositório. |

## Ambiente local de desenvolvimento

Consulte [DOCKER-HELP.md](DOCKER-HELP.md) para usar o ambiente Docker local.

## Testes

```bash
python -m pytest -q
```


## Motor de detecção de vazamento (`detection/`)

O motor calcula `anomaly_detected` em `consumption_summary` e cria alertas em `alerts_history` quando recebe novas janelas de consumo por MongoDB Change Streams. Usa regras explicáveis baseadas em fluxo contínuo, consumo de madrugada e desvios da baseline estatística por usuário e hora. Detalhes em [`detection/README.md`](detection/README.md).

O `LeakAgent` de `delta-artificial-intelligence` consome os alertas calculados por este motor.

## `core/`

O módulo `core/` reúne a configuração (`.env`), conexões com PostgreSQL (`core/db_postgres.py`) e MongoDB (`core/db_mongo.py`), além das estruturas de dados em `core/models.py`.
