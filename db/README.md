# `db/` — bootstrap dos bancos locais de desenvolvimento

Estes arquivos servem **só** para `docker-compose.dev.yml` subir um Postgres e um
MongoDB locais já populados. **Não** são fonte de verdade de schema nem de
modelagem.

## `postgres-init/` — cópias do `delta-sql-database`

Rodam em ordem alfabética na primeira inicialização do container
(`/docker-entrypoint-initdb.d`):

| Arquivo local | Origem em `delta-app-ofc/delta-sql-database` |
|---|---|
| `01-schema.sql` | `script-schema.sql` (cria as 12 tabelas) |
| `02-fn_get_property_classification.sql` | `functions/fn_get_property_classification.sql` |
| `03-dataload.sql` | `script-dataload.sql` (~200 usuários e dados verossímeis) |

O motor de detecção só usa `tb_user_property`/`tb_property.classification`
(via `fn_get_property_classification`), mas o schema precisa das 12 tabelas
inteiras por causa das foreign keys. Cópia feita a partir do commit `35becd9`
do `delta-sql-database`. O schema real continua sendo mantido lá — se ele
mudar, estas cópias precisam ser re-sincronizadas (não edite-as à mão).

## `mongo-init/seed.js` — copiado do `delta-artificial-intelligence`

Mesmo seed de teste usado lá (usuários 11–15), reaproveitado aqui pra ter um
ambiente de dev local com cenários realistas (incl. um de vazamento contínuo
de madrugada, útil pra testar `detection/watcher.py` manualmente).
