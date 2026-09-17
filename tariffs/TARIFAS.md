# Atualização anual da tarifa por região e categoria

`tarifas-YYYY.json` guarda os valores de tarifa (R$/m³, coluna água, faixa
21-50 m³) usados por `update_tariffs.py` pra atualizar `tb_region_rate` uma
vez ao ano. As 5 regiões (`tb_region`) representam áreas com tarifa Sabesp
realmente diferente — não as 5 zonas da Grande SP, que cobram o mesmo preço
entre si (confirmado nas fontes abaixo).

## Fontes (tarifas-2026.json)

- [Nota Técnica do 1º Reajuste Tarifário da Sabesp — URAE-1 Sudeste, ARSESP, nov/2025, vigente jan/2026](https://www.arsesp.sp.gov.br/Documentosgerais/NT_1__REAJUSTE_TARIFARIO_DA_SABESP__Tarifa_Aplicacao___URAE1___assinado.pdf)
- [Tabela Geral de Tarifas da Sabesp, ARSESP](http://www.arsesp.sp.gov.br/ArquivosRegulamentacao/Tarifas/Saneamento/tabela%20de%20tarifas-sabesp-geral.pdf)

## Metodologia

- Coluna "Água", faixa de consumo 21-50 m³.
- **Categorias com sub-faixas** (Residencial Social e Residencial
  Vulnerável/Favela, que na tabela oficial têm "21 a 30" e "31 a 50"
  separados): usamos a média simples das duas sub-faixas, arredondada com
  `Decimal` + `ROUND_HALF_UP` (mesma convenção do resto do projeto). Isso é
  uma simplificação — a tarifa real é progressiva por sub-faixa, não um
  valor único — assumida deliberadamente pra caber no modelo de dados atual
  (uma tarifa por m³ por combinação região/categoria).
- **Residencial Especial / Comercial Especial**: a Sabesp só publica tarifa
  própria pra essas categorias em contratos municipais específicos (Lins,
  Presidente Prudente, Adamantina/Pirapozinho). Nas regiões onde não existe
  tarifa "Especial" publicada (Grande SP e o grupo de Bragança Paulista, e a
  metade que falta em Lins/Adamantina-Pirapozinho), usamos o valor da
  categoria "Normal" equivalente (Residencial Normal ou Comercial
  Normal/Industrial) como aproximação. Essa é uma limitação conhecida, não
  um dado real — documentada aqui de propósito.

## As 5 regiões

| Região | Tabela fonte |
|---|---|
| `GRANDE_SP` | Tabela 1 (unidades OC/OL/OO/ON/OS + Guararema + Santa Isabel) |
| `LINS` | Tabela 10 (exclusiva do município) |
| `PRESIDENTE_PRUDENTE` | Tabela 5 (base) + Tabela 8 (Residencial/Comercial Especial) |
| `ADAMANTINA_PIRAPOZINHO` | Tabela 5 (base) + Tabela 7 (Comercial Especial) |
| `BRAGANCA_PAULISTA` | Tabela 2 (Bragança Paulista, Joanópolis, Nazaré Paulista, Pedra Bela, Pinhalzinho, Piracaia, Socorro, Vargem) |

## Como atualizar todo ano

1. Buscar a tabela tarifária vigente da ARSESP/Sabesp (mesmas fontes acima,
   ou a Nota Técnica de reajuste do ano corrente).
2. Criar um novo `tarifas-YYYY.json` com os 5×8 valores, seguindo a mesma
   metodologia (sub-faixas em média, categorias "Especial" sem tabela
   própria usando o valor "Normal").
3. Rodar `python update_tariffs.py tarifas-YYYY.json` (dry-run, só mostra o
   que mudaria) e depois `python update_tariffs.py tarifas-YYYY.json
   --apply --initial-validity YYYY-01-01` pra gravar de fato, via
   `sp_change_region_rate`.
