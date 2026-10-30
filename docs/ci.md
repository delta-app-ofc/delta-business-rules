# CI técnico

O workflow `.github/workflows/test.yml` executa, em pull requests e por acionamento manual, a suíte pytest em Python 3.12 no Ubuntu. Uma falha na instalação ou nos testes reprova o job. O workflow de governança de PR continua independente.

Para executar localmente, com Python 3.12:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes atuais exercitam a lógica de detecção com dados locais; não verificam conexões reais com PostgreSQL ou MongoDB, Change Streams nem implantação.
