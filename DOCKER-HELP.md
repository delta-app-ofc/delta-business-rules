# Docker — delta-business-rules

## Objetivo

Subir bancos locais para desenvolvimento manual. A suíte Python isolada pode ser executada sem esses bancos.

## Pré-requisitos

Docker Engine em execução e Docker Compose v2. Execute os comandos na raiz deste repositório. Os exemplos usam uma identificação de projeto própria para isolar containers e volumes.

## Executar

```bash
docker compose -p delta-business-rules-dev -f docker-compose.dev.yml config --quiet
docker compose -p delta-business-rules-dev -f docker-compose.dev.yml up -d --wait
docker compose -p delta-business-rules-dev -f docker-compose.dev.yml ps
# Com as dependências Python instaladas:
python -m pytest -q
# Ao terminar:
docker compose -p delta-business-rules-dev -f docker-compose.dev.yml down
```

## Conferir o resultado e encerrar

PostgreSQL: `127.0.0.1:5435`; MongoDB: `127.0.0.1:27019`. As variáveis `POSTGRES_HOST_PORT` e `MONGO_HOST_PORT` permitem escolher outras portas; alinhe as URLs da aplicação à escolha. Copie `.env.example` para `.env` e configure apenas os serviços que utilizará. Para o cliente Mongo no host, use `mongodb://localhost:27019/?directConnection=true`. Se trocar a porta, atualize também a URI.

Espere os bancos ficarem `healthy`. Testes unitários aprovados não confirmam uma conexão real da aplicação com os bancos. Os dados são preservados após `down`; scripts de inicialização do PostgreSQL só executam em volume vazio. A primeira utilização dos volumes nomeados não importa dados de antigos volumes anônimos.

Para diagnosticar falhas de um serviço Compose, use `docker compose -p <projeto> -f <arquivo> ps -a` e `docker compose -p <projeto> -f <arquivo> logs <serviço>`, com o mesmo projeto e arquivo da execução.

`down` preserva volumes nomeados. Só use `down -v` depois de conferir o nome do projeto e confirmar que seus dados são descartáveis. Não remova volumes de outros ambientes.

O seed do Mongo só é aplicado depois da eleição do primário e se os databases locais de app e telemetria ainda não tiverem coleções. Se houver dados locais, o seed é ignorado para preservá-los.
