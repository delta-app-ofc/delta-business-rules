"""Acesso de LEITURA ao PostgreSQL cadastral — só o que as regras de negócio
precisam. Espelha o schema do repositório delta-sql-database (fonte de
verdade); ver db/postgres-init para as cópias de bootstrap usadas em dev.
"""

from __future__ import annotations

import psycopg2

from core.config import DATABASE_URL, HOST_DB, NAME_DB, PASSWORD_DB, PORT_DB, USER_DB


def get_conn():
    """Abre e devolve uma conexão com o Postgres. Quem chama é responsável por fechar."""
    if all((HOST_DB, PORT_DB, USER_DB, PASSWORD_DB, NAME_DB)):
        return psycopg2.connect(
            host=HOST_DB,
            port=PORT_DB,
            user=USER_DB,
            password=PASSWORD_DB,
            dbname=NAME_DB,
        )
    return psycopg2.connect(DATABASE_URL)


def get_user_property_id(user_id: int) -> int | None:
    """Id da (primeira) propriedade vinculada ao usuário, ou None."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT property_id
              FROM tb_user_property
             WHERE user_id = %s
             ORDER BY id
             LIMIT 1;
            """,
            (user_id,),
        )
        row = cur.fetchone()
        return int(row[0]) if row is not None else None
    finally:
        cur.close()
        conn.close()


def get_property_classification(user_id: int) -> str | None:
    """Classificação (RESIDENCIAL/COMERCIAL) da (primeira) propriedade do
    usuário, ou None se ele não tiver propriedade. Usada pelo motor de
    detecção (detection/) para não aplicar a regra de madrugada a
    propriedades comerciais/industriais.
    """
    property_id = get_user_property_id(user_id)
    if property_id is None:
        return None

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT fn_get_property_classification(%s);", (property_id,))
        row = cur.fetchone()
        return str(row[0]) if row is not None and row[0] is not None else None
    finally:
        cur.close()
        conn.close()
