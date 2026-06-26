# CHANGELOG — cs-retrospectiva-ropre-quarter

## [v1.1.3] — 2026-06-26
### Funil do quarter via Growthpack (CSV)
- `_fetch-breakeven-quarter.mjs`: export CSV público (sem gws) + parser automático
- Inside Sales: projetado (aba Funil de vendas) + realizado (soma Investimento Meta abr–jun)
- E-commerce sem aba Breakeven: fallback receita cockpit
- `parseNum` corrigido para decimal API vs formato BR
- TROPM Q2: funil preenchido no HTML; e-commerce: receita via cockpit
- Docs: `fontes-mcp.md` § J, `operacao-runtime.md`, `template-output.md`

## [v1.1.2] — 2026-06-26
### Ekyte hyperlinks + campanha/conjunto
- Entregas Ekyte: `<a href="https://app.ekyte.com/#/tasks/list/{id}/edit">` no detalhe
- Seção 4: nome completo da campanha (`campaignName`) + tabelas de **conjuntos** (`byAdset` / `groupName`)
- `_fetch-ekyte.mjs` → `_data/{TICKER}-ekyte.json`
- `_run-fetch.mjs`: agrega `byAdset` por mês e total Q

## [v1.1.1] — 2026-06-26
### Cliente vs V4 + Ekyte visual
- Seção 7 em 4 blocos: 7a síntese IA · 7b **só cliente** · 7c **conquistas V4** · 7d quantitativo
- Regra explícita: não misturar speakers; cockpit `summary_reasoning` não vai em verbatim
- Seção 6 Ekyte: resumo por tipo (tabela) + detalhe agrupado por tag `[DE]`/`[CA]`/etc.
- `_build-html.py`: `render_ekyte_visual`, `ekyte_conquistas_bullets`, conquistas objetivas em 7c

## [v1.1.0] — 2026-06-26
### Piloto Q2 real (Inside Sales + E-commerce)
- Run end-to-end via MCP: quarter paginado abr–jun, HTML gerado com dados reais
- `references/operacao-runtime.md`: gotchas parser NEKT (`data.items`), busca cockpit, Ekyte, MCP Cursor
- Layout: Projetado → Realizado (esq→dir); tabela mensal + Total Q; ROAS+CPA e-commerce
- Engajamento C:4 avaliado por custo/engajamento (chamada extra actionTypes)
- Divergência NEKT leads vs cockpit funil documentada e renderizada
- Scripts piloto: `_fetch-mcp.mjs`, `_run-fetch.mjs`, `_build-html.py`
- Outputs: HTML de retrospectiva por ticker/quarter

## [v1.0.0] — 2026-04-14
- Versão inicial com 8 seções, pilares, template HTML, protótipos
