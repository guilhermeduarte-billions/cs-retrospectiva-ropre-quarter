# Operação em runtime — aprendizados do piloto Q2/2026

Validado em jun/2026 com projetos **Inside Sales** (Meta leads) e **E-commerce** (Meta purchases).

## MCP no Cursor vs script auxiliar

- O servidor `user-cockpit` pode aparecer como **errored** no Cursor. Se `CallMcpTool` falhar, use o script local:
  - `scripts/_fetch-mcp.mjs` (neste repo)
  - Credenciais via env (`MCP_COCKPIT_JWT`, `MCP_GATEWAY_TOKEN`) — **nunca** commitar
  - Protocolo: `initialize` → `notifications/initialized` (sem id) → `tools/call`
- Pipeline completo de teste:
  1. `node _run-fetch.mjs` — cockpit + NEKT por mês + quarter (**inclui `byAdset` e `byAd`**)
  2. `node _fetch-ekyte.mjs` — entregas com `id` para hyperlink
  3. `node _fetch-breakeven-quarter.mjs {TICKER}` — funil quarter via CSV da planilha Growthpack
  4. `python3 _build-html.py` — renderiza HTML (nomes completos de campanha/conjunto)

## Breakeven / Growthpack (`_fetch-breakeven-quarter.mjs`)

| Problema | Correção |
|----------|----------|
| `gws sheets` sem scope | Usar **export CSV público** (`/export?format=csv&gid=`) quando a planilha permite |
| Nomes truncados no Google Docs | `camp_display` — tokens legíveis sem colchetes (`C:6 · FORM NATIVO · …`) |
| Projetado vs realizado | **Não** misturar com cockpit MTD — `paid_traffic_*` é mês corrente |
| Números cockpit com ponto decimal | `parseNum` deve distinguir `1577202.5` (API) de `26.000,00` (BR) |
| Aba Projeção | Descoberta automática: scan de gids no `htmlview` até achar "Funil de vendas" |

## Gotchas NEKT (`flow_media_conversion_summary`)

| Problema | Correção |
|----------|----------|
| Parser retorna 0 linhas | Linhas vêm em **`response.data.items`**, não `rows` |
| Abr vazio para projeto novo | Normal se `projectStartDate` > início do mês — marcar parcial |
| Leads NEKT ≠ leads cockpit | **Sinalizar divergência** — NEKT = plataforma; cockpit = funil manual |
| Engajamento sem actions | Chamada extra com `actionPresets: ["all"]` + `actionTypes` brutos |
| E-commerce purchase | Só `actions.purchase` / `actionValues.purchase` para ROAS e CPA |

## Gotchas Cockpit (`cockpit_query_table`)

| Problema | Correção |
|----------|----------|
| `search` com ticker curto retorna vazio | Usar trecho do **nome** do cliente ou `cockpit_get_project` com `documentId` |
| Flag/HS desatualizado | Reler cockpit no dia do run |

## Gotchas Ekyte (`ekyte_list_tasks`)

| Problema | Correção |
|----------|----------|
| `workspaceId` do cockpit ≠ tasks do cliente | Validar títulos; preferir **`textSearch`** + `textKey: 300` + datas do quarter |
| Lista poluída | Filtrar ATWPP/weekly/sprint; manter `[DE]`, `[LP]`, `[PC]`, `[GT]`, GO LIVE |

## BigQuery (seção 7)

- Sem BigQuery: usar **slot** para verbatim — cockpit `summary_reasoning` só como apoio para 7a.
- Com BigQuery: `consultar_calls_bigquery` + filtro do quarter + `include_transcription_excerpt: true`.
