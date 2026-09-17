"""Atualiza tb_region_rate (região x categoria) a partir de um JSON anual
de tarifas — ver tariffs/README.md para a fonte e a metodologia dos valores.

Dry-run por padrão (só mostra o que mudaria); passe --apply para gravar de
fato, via sp_change_region_rate.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from core.db_postgres import get_conn


def carregar_tarifas(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def resolver_ids(conn) -> tuple[dict[str, int], dict[str, int]]:
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, id FROM tb_region;")
        regioes = dict(cur.fetchall())

        cur.execute("SELECT name, id FROM tb_property_classification;")
        categorias = dict(cur.fetchall())

        return regioes, categorias
    finally:
        cur.close()


def imprimir_relatorio(tarifas: dict, regioes: dict[str, int], categorias: dict[str, int]) -> None:
    for nome_regiao, valores in tarifas["regioes"].items():
        region_id = regioes.get(nome_regiao)
        for nome_categoria, valor in valores.items():
            if nome_categoria == "tabela_fonte":
                continue
            classification_id = categorias.get(nome_categoria)
            valor_dec = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            status = "OK" if region_id and classification_id else "SEM ID NO BANCO"
            print(f"  [{status}] {nome_regiao} / {nome_categoria}: R$ {valor_dec}/m³")


def aplicar(tarifas: dict, regioes: dict[str, int], categorias: dict[str, int], initial_validity: date, conn) -> int:
    cur = conn.cursor()
    aplicadas = 0
    try:
        for nome_regiao, valores in tarifas["regioes"].items():
            region_id = regioes.get(nome_regiao)
            if region_id is None:
                print(f"  [PULADO] região desconhecida: {nome_regiao}")
                continue

            for nome_categoria, valor in valores.items():
                if nome_categoria == "tabela_fonte":
                    continue

                classification_id = categorias.get(nome_categoria)
                if classification_id is None:
                    print(f"  [PULADO] categoria desconhecida: {nome_categoria}")
                    continue

                valor_dec = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                cur.execute(
                    "CALL sp_change_region_rate(%s, %s, %s, %s);",
                    (region_id, classification_id, valor_dec, initial_validity),
                )
                aplicadas += 1

        conn.commit()
        return aplicadas
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo_tarifas", type=Path, help="ex: tariffs/tarifas-2026.json")
    parser.add_argument("--apply", action="store_true", help="grava as tarifas no banco (senão só mostra o que faria)")
    parser.add_argument("--initial-validity", type=str, default=None, help="data de início de vigência, formato YYYY-MM-DD (padrão: fonte.vigencia do JSON)")
    args = parser.parse_args()

    tarifas = carregar_tarifas(args.arquivo_tarifas)

    conn = get_conn()
    try:
        regioes, categorias = resolver_ids(conn)

        print(f"Fonte: {tarifas['fonte']['descricao']}")
        print(f"Faixa: {tarifas['fonte']['faixa_m3']} m³ | Coluna: {tarifas['fonte']['coluna']}\n")

        imprimir_relatorio(tarifas, regioes, categorias)

        if not args.apply:
            print("\nDry-run — nada foi gravado. Rode com --apply para aplicar.")
            return

        initial_validity_str = args.initial_validity or tarifas["fonte"]["vigencia"]
        initial_validity = datetime.strptime(initial_validity_str, "%Y-%m-%d").date()

        aplicadas = aplicar(tarifas, regioes, categorias, initial_validity, conn)
        print(f"\n[OK] {aplicadas} combinações região/categoria atualizadas (vigência a partir de {initial_validity}).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
