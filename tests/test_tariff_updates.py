from datetime import date
from decimal import Decimal

import pytest

import update_tariffs


class FakeCursor:
    def __init__(self, *, failure=None, rows=()):
        self.failure = failure
        self.rows = list(rows)
        self.calls = []
        self.closed = False

    def execute(self, query, parameters=None):
        if self.failure is not None:
            raise self.failure
        self.calls.append((query, parameters))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, *, failure=None, rows=()):
        self.fake_cursor = FakeCursor(failure=failure, rows=rows)
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def test_apply_skips_unknown_ids_rounds_money_and_commits(capsys):
    connection = FakeConnection()
    tariffs = {
        "regioes": {
            "SUDESTE": {
                "RESIDENCIAL_NORMAL": "1.255",
                "INEXISTENTE": "4.00",
                "tabela_fonte": "faixa base",
            },
            "REGIAO AUSENTE": {"RESIDENCIAL_NORMAL": "2.00"},
        }
    }

    applied = update_tariffs.aplicar(
        tariffs,
        {"SUDESTE": 3},
        {"RESIDENCIAL_NORMAL": 8},
        date(2026, 1, 1),
        connection,
    )

    assert applied == 1
    assert connection.fake_cursor.calls == [
        (
            "CALL sp_change_region_rate(%s, %s, %s, %s);",
            (3, 8, Decimal("1.26"), date(2026, 1, 1)),
        )
    ]
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert connection.fake_cursor.closed is True
    output = capsys.readouterr().out
    assert "categoria desconhecida: INEXISTENTE" in output
    assert "região desconhecida: REGIAO AUSENTE" in output


def test_apply_rolls_back_and_closes_cursor_after_database_error():
    connection = FakeConnection(failure=RuntimeError("procedure failed"))
    tariffs = {"regioes": {"SUDESTE": {"RESIDENCIAL_NORMAL": "1.25"}}}

    with pytest.raises(RuntimeError, match="procedure failed"):
        update_tariffs.aplicar(
            tariffs,
            {"SUDESTE": 3},
            {"RESIDENCIAL_NORMAL": 8},
            date(2026, 1, 1),
            connection,
        )

    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert connection.fake_cursor.closed is True


def test_resolver_ids_reads_both_lookups_and_closes_cursor():
    cursor = FakeCursor(rows=[("SUDESTE", 3), ("RESIDENCIAL_NORMAL", 8)])

    class Connection:
        def cursor(self):
            return cursor

    regions, categories = update_tariffs.resolver_ids(Connection())

    assert regions == {"SUDESTE": 3, "RESIDENCIAL_NORMAL": 8}
    assert categories == {"SUDESTE": 3, "RESIDENCIAL_NORMAL": 8}
    assert len(cursor.calls) == 2
    assert "tb_region" in cursor.calls[0][0]
    assert "tb_property_classification" in cursor.calls[1][0]
    assert cursor.closed is True


def test_print_report_rounds_values_and_marks_missing_lookup_ids(capsys):
    update_tariffs.imprimir_relatorio(
        {"regioes": {"SUDESTE": {"RESIDENCIAL_NORMAL": "1.235"}}},
        {"SUDESTE": 3},
        {"RESIDENCIAL_NORMAL": 8},
    )

    assert "[OK] SUDESTE / RESIDENCIAL_NORMAL: R$ 1.24/m³" in capsys.readouterr().out
