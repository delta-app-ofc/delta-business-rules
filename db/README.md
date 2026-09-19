# `db/` — bootstrap dos bancos locais de desenvolvimento

Estes arquivos servem **só** para `docker-compose.dev.yml` subir um Postgres e um
MongoDB locais já populados. **Não** são fonte de verdade de schema nem de
modelagem.

## `postgres-init/` — cópias do `delta-sql-database`

Rodam em ordem alfabética na primeira inicialização do container
(`/docker-entrypoint-initdb.d`):

| Arquivo local | Origem em `delta-app-ofc/delta-sql-database` |
|---|---|
| `01-schema.sql` | `script-schema.sql` (cria as tabelas) |
| `02-fn_get_property_classification.sql` | `functions/fn_get_property_classification.sql` |
| `03-fn_get_property_classification_group.sql` | `functions/fn_get_property_classification_group.sql` |
| `04-dataload.sql` | `script-dataload.sql` (~200 usuários e dados verossímeis) |

O motor de detecção usa `tb_user_property`/`tb_property.classification_id`
(via `fn_get_property_classification_group`, que devolve o grupo
RESIDENCIAL/COMERCIAL, não a categoria específica), mas o schema precisa das
tabelas inteiras por causa das foreign keys. O schema real continua sendo
mantido no `delta-sql-database` — se ele mudar, estas cópias precisam ser
re-sincronizadas (não edite-as à mão).

## `mongo-init/seed.js` — copiado do `delta-artificial-intelligence`

Mesmo seed de teste usado lá (usuários 11–15), reaproveitado aqui pra ter um
ambiente de dev local com cenários realistas (incl. um de vazamento contínuo
de madrugada, útil pra testar `detection/watcher.py` manualmente).
