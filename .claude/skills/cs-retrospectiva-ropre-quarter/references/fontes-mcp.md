# Fontes MCP — chamadas canônicas e gotchas

Servidor MCP: `flow` (ou `cockpit` — espelham as mesmas tools). `platform` em toda tool de mídia: `"meta_ads"` ou `"google_ads"`.

## A. Resolver coordenador e projetos (onboarding)
- `cockpit_list_coordinators` → casar a pessoa (nome/e-mail) → `documentId`.
- `cockpit_query_table` com `filterByUser="<documentId>"`, `filterByCategory="all"`, `filterByStatus="all"` → projetos da pessoa. (Ou `cockpit_list_projects`.)

## B. Contexto do projeto (1 chamada resolve quase tudo)
`cockpit_query_table` com `search="<nome>"` **e `resolveCalculations: true`**, `pageSize: 5`.
Atenção: `search` com `&` pode zerar — use o trecho simples do nome. Retorna `data[].healthScoreTable` com:

| Bloco | Campos |
|---|---|
| Identidade | `documentId`, `name`, `ticker`, `squad[].name`, `tier`, `phase`, `fee`, `project_segment` |
| Equipe | `project_coordinator`, `project_manager`, `account_manager`, `designer`, `copywriter`, `paid_media_specialist`, `social_media_manager`, `crm_analyst`, `data_analyst` (+ `projectTeam[]` com nomes/e-mails) |
| Negócio | `project_maturity_model_business` (Inside Sales / Ecommerce), `project_maturity_sales_model` (B2B/B2C), `project_maturity_product_ticket` |
| CRM | `paid_traffic_project_crm`, `paid_traffic_mql_sql_criteria` |
| Flag/HS | `algorithm_flag`, `algorithm_health_avg_score`, `algorithm_customer_care_status` |
| Funil | `paid_traffic_{leads,mql,sql,sales,revenue}_{milestone,realized,pacing}_{qty,pct}` |
| Resultado | `results_goal_aligned_with_client`, `results_goal_qty`, `results_goal_reached_qty`, `results_goal_reached_pct`, `results_breakeven_*`, `results_contribution_margin_pct` |
| Budget | `campaigns_budget_current_{meta,google,linkedin}_qty`, `campaigns_budget_pacing_{...}_pct` |
| Cliente | `call_transcription_sentiment_synthesis_score`, `call_transcription_verticals_{tasks,copy,design,traffic,social}_score`, `call_transcription_summary_reasoning`, `call_transcription_opportunity_*`, `whatsapp_group_sentiment_synthesis`, `whatsapp_group_status_{risco,atendimento}` |
| CSAT/NPS | `csat_nps_value`, `csat_v4_score`, `csat_service_score`, `csat_campaigns_score`, `csat_copy_score`, `csat_design_score`, `csat_results_score`, `csat_observations` |
| Entregas | `deliveries_sla_ekyte_launched_bool`, `deliveries_commercial_tracking_*`, `deliveries_tasks_status`, `deliveries_project_anomaly*`, `deliveries_ropre_last_checkin_link` |

> ⚠️ Muitos campos do cockpit são **preenchidos à mão no FLOW** (funil MQL/SQL/Vendas, CSAT/NPS). Se `null`, vira **slot** — não invente.
> ⚠️ **Divergências**: já houve `results_goal_reached_qty=0` com `paid_traffic_revenue_realized=26000`. Mostre os dois e sinalize.

## C. Canais conectados
`flow_project_data_list_connections` com `projectDocumentId`. Retorna por conexão: `platform` (meta_ads/google_ads), `status` (connected/syncing/error), `accountId`, `capabilities[]`. **Só puxe performance do canal que estiver `connected`.** Budget Google no cockpit **não** implica dados Google no NEKT.

## D. Mídia — entrega
`flow_media_query_reports` (`projectDocumentId`, `platform`, `period:{startGte,endLt}`, `pagination:{limit:500,offset}`). `metrics`: COST, CLICKS, IMPRESSIONS, REACH, CPC, CPM, CTR. Granular ad×dia.

> ⚠️ **`flow_media_conversion_summary` retorna linhas em `data.items`** (schema `flow.project_data.query.v1`), não em `rows`. Paginar até `items.length < limit`.

## E. Mídia — conversão (a tool principal)
`flow_media_conversion_summary` (`period`, `pagination`, opcional `filters.campaignId`).
- `actionPresets`: `leads` · `leads_site` · `conversations` · `purchases` · `all`. **`all` = todos os PRESETS, não todas as actionTypes** — para Page View/Vídeo passe `actionTypes` brutos.
- `actionTypes` (lista bruta, máx 50): ex. `["lead","landing_page_view","video_view","link_click","post_engagement"]`.
- KPIs por linha em **`actions`**, **`costPerAction`**, **`actionValues`** (NÃO em `metrics`).

| KPI | Campo |
|---|---|
| Leads | `actions.lead` (não somar `onsite_conversion.lead_grouped`) |
| CPL | `SUM(COST)/SUM(actions.lead)` |
| Conversas | `actions.onsite_conversion.messaging_conversation_started_7d` (preset `conversations`) |
| Page View | `actions.landing_page_view` |
| Hook Rate | `actions.video_view` / `IMPRESSIONS` |
| Connect Rate | `actions.landing_page_view` / `actions.link_click` |
| Vendas (e-com) | `actions.purchase` (só `purchase`, não `omni_/web_in_store_/offsite_`) |
| Receita (e-com) | `actionValues.purchase` |
| ROAS | `SUM(actionValues.purchase)/SUM(COST)` |
| CPA (e-com) | `costPerAction.purchase` |

**Ramificação por modelo** (`project_maturity_model_business`): Inside Sales → preset `leads`; E-commerce → preset `purchases`.

### E.1 Métricas por objetivo da campanha (`goal`) — regra crítica
**Nunca avalie uma campanha pela métrica de outro objetivo.** Avalie cada uma pela métrica do seu `goal` e só compare dentro do mesmo objetivo.

| `goal` | Métrica primária | Actions / campos |
|---|---|---|
| OUTCOME_LEADS | Leads, CPL | `actions.lead` |
| OUTCOME_SALES / Conversão | Compras, ROAS, CPA | `actions.purchase`, `actionValues.purchase` |
| OUTCOME_TRAFFIC | Cliques no link, Page View, CPC, Connect Rate | `actions.link_click`, `actions.landing_page_view` |
| OUTCOME_ENGAGEMENT / impulsionamento / Visitas ao Perfil | **Custo por engajamento**, reações, saves, video views, **custo por seguidor** | `post_engagement`, `page_engagement`, `post_reaction`, `onsite_conversion.post_save`, `like`, `comment`, `video_view` |
| OUTCOME_AWARENESS | Alcance, CPM, frequência | `REACH`, `CPM` |
| Mensagens (WhatsApp) | Conversas, custo por conversa | `onsite_conversion.messaging_conversation_started_7d` |

Cálculos de engajamento: custo/engajamento = COST/`post_engagement`; custo/seguidor ≈ COST/`like` (proxy); custo/save = COST/`onsite_conversion.post_save`; custo/video view = COST/`video_view`.

> ⚠️ Resultados grandes (>~25k tokens) são salvos em arquivo pelo harness — agregue com um script (python: `json.loads`, somar por `dimensions.campaignName`/`adName`/`period.startAt[:7]`).

## F. Inventário e criativo
- `flow_media_campaign_summary` → `dimensions.status`, `dimensions.goal` (OUTCOME_LEADS/OUTCOME_TRAFFIC/…), `metrics.BUDGET`.
- `flow_media_group_summary` / `flow_media_ad_summary` (filtram por `campaignId`/`groupId`).
- `flow_media_creative_summary` → `title`, `body` (copy completa). **Não traz imagem/preview** → preview = slot (testar `flow_media_list_tables`+`flow_media_query`).

## G. Entregas (Ekyte)
1. Resolver workspace: `external_integrations` do cockpit (campo `data.id`) **ou** `ekyte_list_projects` com `textSearch`.
2. `ekyte_list_tasks`: `situation: "30"` (concluído), `concludedDateStart`/`concludedDateEnd` = quarter, `limit: 200`.
3. Se `workspaceId` retornar tasks de outro cliente → usar **`textSearch` + `textKey: 300`** com nome do cliente + `concludedDateStart/End` do quarter.
4. Filtrar ruído operacional (ATWPP, weekly, sprint, atendimento diário); listar entregas `[DE]`, `[LP]`, `[PC]`, `[GT]`, GO LIVE, campanhas.
5. **Listar cada tarefa** (data + título + **link** `https://app.ekyte.com/#/tasks/list/{id}/edit`) — não resumir em contagem.

## H. Cliente — BigQuery (fonte primária para seção 7)
`mcp__bigquery-calls__consultar_calls_bigquery` e `mcp__bigquery-whatsapp__*` (`localize_project` casa ticker→project).
- Filtrar pelo **período do quarter** (não só o último mês).
- `include_transcription_excerpt: true` para o agente ler transcrições.
- **Separar speakers:** na transcrição, identificar linhas do **cliente** vs **V4/Colli** (coord, tráfego, design, AM). Se o campo não tiver speaker → inferir com cuidado ou slot.
- **7b** = verbatim **somente cliente** (elogios | atenção), formato `"frase"` — **[Cliente · Call AAAA-MM-DD]**.
- **7c** = verbatim **somente V4** na call **ou** conquistas objetivas (`[NEKT]`, `[Ekyte]`, `[Cockpit]`).
- **7a** = síntese neutra do agente (evolução do sentimento no quarter).
- Cockpit (`call_transcription_summary_reasoning`) = pista interna para 7a — **não** colar em 7b/7c.

## I. Agregação temporal (quarter)
- Paginar NEKT para **cada mês** do quarter; somar em `Total Q`.
- Agregar rankings de campanha/criativo no **nível do quarter** (soma de abr+mai+jun), mas citar variação mensal na síntese quando relevante.
- ⚠️ **Funil da seção 2:** NÃO usar `paid_traffic_*` do cockpit como quarter — são **MTD** (mês corrente). Quarter = planilha Breakeven (§ J) ou `results_goal_*` para receita e-commerce.

## J. Breakeven / Growthpack (funil do quarter — seção 2)

Link: `paid_traffic_growthpack_updated_link` no cockpit (`gid=` na URL = aba Breakeven mensal).

**Fetch automático (piloto):** `node _fetch-breakeven-quarter.mjs {TICKER}`

| Método | Quando |
|--------|--------|
| **Export CSV público** | Primário — `https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid={gid}` (não precisa gws) |
| `gws sheets +read` | Fallback se export bloqueado (requer scope Sheets) |

**Layout Inside Sales (Growthpack):**

| Dado | Onde na planilha |
|------|------------------|
| Realizado Q | Aba do `gid` do link — bloco **Investimento Meta**, somar cols **abr+mai+jun** |
| Projetado Q | Aba com **Funil de vendas** — colunas finais: qty + etapa |
| Receita projetada | `results_goal_qty` do cockpit (meta alinhada) |

**E-commerce:** growthpack pode ser só planejamento de campanhas — sem aba Breakeven mensal. Fallback: `paid_traffic_revenue_milestone_qty` / `paid_traffic_revenue_realized_qty`.

**Gotchas parseNum:** cockpit retorna decimal com ponto (`1577202.5`); planilha BR usa `26.000,00`. Não remover ponto decimal único.

Ver `references/operacao-runtime.md`.
