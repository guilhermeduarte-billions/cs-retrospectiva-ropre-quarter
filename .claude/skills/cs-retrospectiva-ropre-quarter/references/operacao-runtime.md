# Operação em runtime — aprendizados do piloto Q2/2026

Validado em 26/jun/2026 com TROPM + UMBRO (Inside Sales + E-commerce).

## MCP no Cursor vs script auxiliar

- O servidor `user-cockpit` pode aparecer como **errored** no Cursor. Se `CallMcpTool` falhar, use o script local:
  - `Brain/Trabalho V4/Projetos/retrospectiva-ropre-quarter/_fetch-mcp.mjs`
  - Lê `~/.config/colli/mcp.env` (`MCP_COCKPIT_JWT`, `MCP_GATEWAY_TOKEN`)
  - Protocolo: `initialize` → `notifications/initialized` (sem id) → `tools/call`
- Pipeline completo de teste:
  1. `node _run-fetch.mjs` — puxa cockpit + NEKT por mês + quarter (**inclui `byAdset` e `byAd`**)
  2. `node _fetch-ekyte.mjs` — entregas com `id` para hyperlink
  3. `node _fetch-breakeven-quarter.mjs {TICKER}` — funil quarter via CSV da planilha Growthpack
  4. `python3 _build-html.py` — renderiza HTML (links Ekyte + campanha/conjunto completos)

## Breakeven / Growthpack (`_fetch-breakeven-quarter.mjs`)

| Problema | Correção |
|----------|----------|
| `gws sheets` sem scope | Usar **export CSV público** (`/export?format=csv&gid=`) — funciona nas planilhas compartilhadas do piloto |
| Nomes truncados a `C:6` no Google Docs | `camp_display` sem truncar — tokens legíveis `C:6 · FORM NATIVO · …` (colchetes somem ao colar no Docs) |
| Projetado vs realizado | **Não** misturar com cockpit MTD — `paid_traffic_leads_realized` em jun/26 = 774 (só mês), quarter planilha = 1.257 |
| Números cockpit com ponto decimal | `parseNum` deve distinguir `1577202.5` (API) de `26.000,00` (BR) |
| Aba Projeção | Descoberta automática: scan de gids no `htmlview` até achar "Funil de vendas" |

**TROPM** spreadsheet `1MeRjy3H2seLAsyY5RPWMXH-4vnkTcSaFk1qUIc1IfVk`: breakeven gid `1422566774`, projeção gid `915232164`.

## Gotchas NEKT (`flow_media_conversion_summary`)

| Problema | Correção |
|----------|----------|
| Parser retorna 0 linhas | Linhas vêm em **`response.data.items`**, não `rows` |
| Abr vazio para projeto novo | Normal se `projectStartDate` > início do mês — marcar parcial |
| Leads NEKT ≠ leads cockpit | **Sinalizar divergência** — NEKT = atribuição plataforma; cockpit = funil comercial manual |
| Engajamento sem actions | Rodar chamada separada com `actionPresets: ["all"]` + `actionTypes` brutos (`post_engagement`, `video_view`, …) |
| E-commerce purchase | Usar só `actions.purchase` / `actionValues.purchase` para ROAS e CPA |

## Gotchas Cockpit (`cockpit_query_table`)

| Problema | Correção |
|----------|----------|
| `search: "TROPM"` retorna vazio | Usar trecho do nome: **`"Tropical"`** ou `cockpit_get_project` com `documentId` |
| `search: "Umbro"` | Funciona |
| Flag desatualizada no protótipo | Reler cockpit no dia do run (TROPM virou **Safe** HS 26,4 em 26/jun) |

## Gotchas Ekyte (`ekyte_list_tasks`)

| Problema | Correção |
|----------|----------|
| `workspaceId` do cockpit ≠ tasks do cliente | Validar títulos; TROPM ws `134937` retornou Biesky misturado — preferir **`textSearch: "Tropical"`** + `textKey: 300` + `concludedDateStart/End` do quarter |
| UMBRO | `workspaceId: "138963"` OK · 160 tasks no Q2 |
| Lista poluída | Filtrar: excluir ATWPP/weekly/sprint/atendimento diário; manter `[DE]`, `[LP]`, `[PC]`, `[GT]`, GO LIVE, campanhas |

## BigQuery (seção 7)

- Piloto usou **slot** para verbatim — cockpit `call_transcription_summary_reasoning` só como apoio.
- Próximo passo: `consultar_calls_bigquery` com filtro Q2 + `include_transcription_excerpt: true`.

## Números de referência Q2/2026 (paginado)

**TROPM** (`mysl8i80hmdevokliirkplu1`, Meta leads):
- Total Q2: R$ 6.959 · 1.267 leads NEKT · CPL R$ 5,49
- Mensal CPL: abr R$ 2,35 → mai R$ 6,58 → jun R$ 5,56
- C:4 engajamento Q2: R$ 1.855 · 32.163 post_engagements · R$ 0,06/eng
- Funil quarter (Growthpack): 1.257 leads · 649 MQL · 124 SQL · 2 vendas · R$ 26k (pacing receita 148%)
- Cockpit MTD (jun): 774 leads · 454 MQL — **não** usar como quarter

**UMBRO** (`tx7tziccepvlr6sqhet3cf0h`, Meta purchases):
- Total Q2: R$ 220.306 · 6.324 compras · ROAS 11,65 · CPA R$ 34,84
- Mensal ROAS: abr 14,15 → mai 10,07 → jun 10,24
- Top Q2: Catálogo ROI Hunter ROAS 29,9 · CPA R$ 12,61
