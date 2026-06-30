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
| GrowthPack | `paid_traffic_growthpack_updated_link` — **link do GrowthPack do projeto** (fallback de descoberta quando não há planilha-mestra do squad; ver § J.0) |

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

Cálculos de engajamento: custo/engajamento = COST/`post_engagement`; custo/seguidor ≈ COST/`like` (proxy — `profile_visit`/`follow` **não** vêm como action no NEKT); custo/save = COST/`onsite_conversion.post_save`; custo/video view = COST/`video_view`. Valores reais validados na C:4 TROPM (jun): 7.220 post_engagements a R$0,10; 447 reações; 31 saves; 18 likes; 3.259 video views.

> ⚠️ Resultados grandes (>~25k tokens) são salvos em arquivo pelo harness — agregue com um script (python: `json.loads`, somar por `dimensions.campaignName`/`adName`/`period.startAt[:7]`).

## F. Inventário e criativo
- `flow_media_campaign_summary` → `dimensions.status`, `dimensions.goal` (OUTCOME_LEADS/OUTCOME_TRAFFIC/…), `metrics.BUDGET`.
- `flow_media_group_summary` / `flow_media_ad_summary` (filtram por `campaignId`/`groupId`).
- `flow_media_creative_summary` → `title`, `body` (copy completa). **Não traz imagem/preview** → preview = slot (testar `flow_media_list_tables`+`flow_media_query`).

### F.1 Keywords Google Ads Search — SÓ NEKT (NÃO-PULÁVEL)

> **Fonte única de mídia = NEKT.** Proibido puxar keywords da API de plataforma (`google-ads` MCP/GAQL). Se o NEKT não entregar, é **slot sinalizado para iteração** — o usuário decide. Ver princípio 11 do SKILL.md.

Para campanhas Search/Display (`platform: "google_ads"`):
1. `flow_media_list_tables` com `projectDocumentId` + `platform: "google_ads"` → inspecionar `tables[]` procurando recurso com `keyword` no nome (ex. `keyword_summary`, `keyword_view`).
2. Se existir: `flow_media_query` com `resource: "<nome>"`, `period` do quarter, campos `keyword_text`/`COST`/`CLICKS`/`CONVERSIONS`/`AVERAGE_CPC`. Ordenar por `CONVERSIONS` DESC, `limit: 200`.
3. Ranking top 10 keywords ✅ (convertem / menor CPL) e bottom 5 ❌ (gastam sem conversão). CPL = COST/CONVERSIONS.
4. **Se `list_tables` não retornar `keyword_*`, OU o flow falhar (ex. "Connection closed"):** renderizar **slot** — "⚠ Keywords pendentes — NEKT não retornou nesta rodada; sinalizar para iteração". **Nunca** contornar pela API.
5. Custo Google em **micros** (`*_COST_MICROS`) → ÷ 1.000.000.

> ⚠️ **O NEKT pode não sincronizar nível de keyword.** O `flow_media_list_tables` retorna os **streams sincronizados** daquela conexão. Em muitas contas Google Ads só vêm `campaigns`, `ad_groups` (adSets), `ads`, `ad_performance` (adInsights) — **sem `keyword_*` nem `search_term_*`**. Nesse caso é **ausência confirmada** (slot legítimo). A iteração correta é pedir ao dono do conector NEKT para incluir o stream de keywords/termos — **não** ir na API.

**OUTMAT OTMT (Q2/2026, confirmado):** `list_tables` da conta 959-833-8321 retornou só `campaigns/ad_groups/ads/ad_performance`. **Sem stream de keyword/search_term** → slot de ausência confirmada. (Google pausado no quarter: R$ 800 abr → R$ 69 mai → R$ 0 jun.)

## G. Entregas (Ekyte)
1. Resolver workspace: `external_integrations` do cockpit (campo `data.id`) **ou** `ekyte_list_projects` com `textSearch`.
2. `ekyte_list_tasks`: `situation: "30"` (concluído), `concludedDateStart`/`concludedDateEnd` = quarter, `limit: 200`.
3. Se `workspaceId` retornar tasks de outro cliente → usar **`textSearch` + `textKey: 300`** com nome do cliente (validado: TROPM ws 134937 misturou Biesky; `textSearch: "Tropical"` funcionou).
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

## J. GrowthPack — Realizado consolidado do quarter (MACRO)

> **Princípio:** o Realizado consolidado do quarter **não existe no FLOW** (cockpit é MTD). Ele mora no **GrowthPack** do projeto. O GrowthPack abre a análise (macro + por canal); o NEKT entra depois (micro) e serve de reconciliação. Acesso à planilha (Drive MCP / CSV público / service account): ver `references/growthpack-acesso.md`.

### J.0 Planilha-mestra do squad (índice → descoberta do GrowthPack)
Cada squad tem **uma planilha-mestra** (configurável; URL é parâmetro de config, não path do Brain). A aba oficial é um índice por projeto. Colunas observadas:

`Coordenacao | Projeto | HS | Antecipacao (HS<=21) | Score Ops | Resultado Flow (Cockpit) | Flag | LT | FEE | Mídia | MC | MRR | Link do Break-even (Antigo) | Link do GrowthPack | Retrospectiva (By AI) | Contexto do projeto (Datas sazonais) | ...`

- **Filtrar `Coordenacao = <usuário>`** → projetos da pessoa, cada um com seu **`Link do GrowthPack`**.
- O `Link do GrowthPack` dá `SPREADSHEET_ID` + `gid` para abrir a planilha do projeto.
- Útil também: `HS`, `Flag`, `Score Ops`, `FEE`, `Mídia` (% de fee em mídia), `Contexto do projeto (Datas sazonais)` — alimentam a Visão geral e a leitura de sazonalidade.

**Fallback de descoberta (sem planilha-mestra) — o FLOW também tem o link.** Se o squad não tem planilha-mestra configurada, ou o projeto não está nela, pegue o link direto do cockpit: campo **`paid_traffic_growthpack_updated_link`** (`cockpit_query_table` com `resolveCalculations: true`). Toda linha de projeto no FLOW carrega esse campo. A partir do link, o fluxo é idêntico (J.1). Ordem de prioridade: **1) planilha-mestra → 2) `paid_traffic_growthpack_updated_link` do FLOW → 3) slot** (só se ambos vazios).

### J.1 GrowthPack do projeto — aba "Acompanhamento Mensal"
Template **GrowthPack 3.0**: meses nas **colunas** (jan/24 … jun/26), indicadores nas **linhas**. Gid padrão da aba **`1422566774`** (confirmar pelo nome da aba — pode variar por projeto).

**Ancorar o quarter pelas colunas certas:** a linha **`Ano`** mislabela alguns 2026 como 2025 — **NÃO confie nela**. Use as linhas **`Data inicial`** / **`Data final`** / **`Mês`** para achar as 3 colunas do quarter (Q2/2026 = `01/04/2026`, `01/05/2026`, `01/06/2026`).

**Mapa de linhas (consolidado — somar/ler nas 3 colunas do quarter):**

| Indicador | Linha na planilha | Uso |
|---|---|---|
| Meta de leads (projetado/mês) | `Meta` | Projetado Q = soma |
| Leads realizados (total) | `Leads` | Realizado Q = soma |
| Atingimento | `% da Meta` | leitura por mês |
| Investimento projetado | `Plano de mídia Mês` | Projetado Q = soma |
| Investimento realizado | `Investimento` | Realizado Q = soma |
| CTR consolidado | `CTR` | |
| Taxa clique→lead | `Taxa de Conversão` | |
| CPL | `Custo por Lead` | conferir com invest/leads |
| Impressões / Cliques | `Impressões` / `Cliques` (bloco "Indicadores V4") | |
| Faturamento / Vendas / MQL / SQL | `Total de Faturamento (manual)`, `Todas as Vendas (manual)`, `Todos os MQLs (manual)`, `Todos os SQLs (manual)` | **preenchidos à mão** — quase sempre "-" → slot |

**Blocos por canal (mesma aba, mais abaixo):**

| Canal | Cabeçalho do bloco | Leads do canal | Invest | CPL |
|---|---|---|---|---|
| Meta Ads | `Investimento Meta` | `On-Facebook Leads` + `Website Leads` | linha `Investimento Meta` | `Custo por Lead Nativo` / `Custo por Lead Site` |
| Google Ads | `Investimento Google` | `Leads` (dentro do bloco Google) | linha `Investimento Google` | `Custo por Lead` (bloco Google) |

### J.2 Reconciliação NEKT vs GrowthPack (obrigatória)
Depois de puxar o NEKT por canal, monte uma tabela: `Métrica | GrowthPack | NEKT paginado | Diferença | Leitura`. Investimento e leads por canal devem bater de perto; diferença pequena = **data de corte** (NEKT até ontem; junho parcial antes de 30/06). **GrowthPack é a base oficial do Realizado**; NEKT é o detalhe e a explicação.

### J.3 Gotchas
- **parseNum:** cockpit retorna decimal com ponto (`1577202.5`); planilha BR usa `26.000,00` e `R$`. Não remova ponto decimal único; trate `-` e vazio como sem-dado (slot), não zero.
- **Junho parcial:** se a data de corte é antes do fim do mês, marque junho como parcial e oriente revalidar após o fechamento.
- **Fallback de link:** se não houver planilha-mestra configurada, `paid_traffic_growthpack_updated_link` do cockpit acha o link do GrowthPack do projeto.
- **E-commerce:** GrowthPack pode não ter aba de acompanhamento de leads (foco em receita). Fallback: receita via `results_goal_*` / `paid_traffic_revenue_*` do cockpit, ROAS/CPA via NEKT.

**EEAA / Emaster (validado Q2/2026):** Projetado 3.687 leads · invest R$ 44.875. Realizado 3.443 leads · invest R$ 45.858 · atingimento 93,4% · CPL R$ 13,32. Por canal: Meta 3.089 leads (CPL R$ 11,90, 80% do invest) · Google 354 (CPL R$ 25,66). NEKT bateu com GrowthPack em leads Meta (3.089=3.089) e invest com diferença de data de corte. Maio foi o mês de gap (77,4% da meta); junho recuperou (105,7%).

## Exemplos reais validados (26/jun/2026) — Q2 paginado

**TROPM** `mysl8i80hmdevokliirkplu1` (Inside Sales, Meta):
- Q2: R$ 6.959 invest · **1.267 leads NEKT** · CPL R$ 5,49
- CPL mensal: abr R$ 2,35 → mai R$ 6,58 → jun R$ 5,56
- C:4 impulsionamento Q2: R$ 1.855 · 32.163 engajamentos · R$ 0,06/eng
- Cockpit funil Q2: 774 leads · 2 vendas · receita R$ 26k (⚠ diverge de NEKT em leads)

**UMBRO** `tx7tziccepvlr6sqhet3cf0h` (E-commerce, Meta):
- Q2: R$ 220.306 · 6.324 compras · ROAS 11,65 · CPA R$ 34,84
- ROAS mensal: abr 14,15 → mai 10,07 → jun 10,24
- Receita quarter (cockpit): projetado R$ 1,58M · realizado R$ 1,51M (96% pacing) — NEKT atribui R$ 2,52M (divergência CRM vs plataforma)

Ver `references/operacao-runtime.md`.
