---
name: cs-retrospectiva-ropre-quarter
description: Gera automaticamente a retrospectiva de Growth Marketing do Quarter de um cliente para as reuniões de ROPRE, cruzando FLOW/NEKT (mídia + conversões Meta/Google), cockpit (contexto, funil, resultado, sentiment, CSAT/NPS, entregas), Ekyte e BigQuery, num HTML limpo (colável no Google Docs) com 8 seções por pilar (Tráfego, Criativo/Copy, Gestão de Projetos, Cliente, CRM/Funil) e uma matriz Problemas|Soluções por integrante. É agnóstica a coordenação/gerência: a pessoa faz onboarding (se identifica → a skill descobre os projetos dela no FLOW) e roda a retro dos seus projetos. ZERO base local — tudo via MCP. Use quando o usuário rodar /cs-retrospectiva-ropre-quarter, pedir pra "fazer a retrospectiva do quarter do cliente X", "montar a retro do ROPRE", "o que deu certo e errado no trimestre", "retrospectiva de growth do cliente", ou preparar o insumo de dados de uma reunião de ROPRE/retrospectiva trimestral.
area: cs
author: guilhermeduarte-billions
version: 1.1.3
---

# cs-retrospectiva-ropre-quarter — Retrospectiva de Growth do Quarter (ROPRE)

Dado um **coordenador**, um **projeto** e um **período (quarter)**, gera um **HTML de retrospectiva** com o que deu certo / o que deu errado / aprendizados por pilar, pronto para a reunião de ROPRE e para colar num Google Docs. A skill **municia a reunião, não decide**: ela traz os dados e os Problemas; as **Soluções/Ações ficam em branco** para o time preencher.

Não confundir com `analise-ropre-quarter` (que **avalia** um ROPRE pronto por rubrica). Esta **gera** o conteúdo a partir de dados reais.

## Princípios inegociáveis
1. **ZERO base local.** Nenhum dado vem de arquivos do Brain (`projetos.yaml`, `Clientes/`, relatórios). **Tudo via MCP** (FLOW cockpit/media, Ekyte, BigQuery). A skill roda para **qualquer coordenação/gerência**.
2. **Proveniência sempre.** Todo dado carrega a fonte entre colchetes — `[NEKT]`, `[Cockpit]`, `[Ekyte]`, `[CRM]`, `[Call AAAA-MM-DD]`, `[WhatsApp]`.
3. **Anti-blefe → slot.** Lacuna nunca vira invenção. Onde falta fonte, renderize um **slot** visível ("⚠ Preencher manualmente — fonte X não conectada"). Nunca deduza número.
4. **Ações são do time.** A skill pré-preenche **Problemas** (a partir dos dados); a coluna **Soluções/Ações fica vazia** (slot) — o time preenche na reunião.
5. **Sinalize divergências.** Se dois campos do FLOW para a mesma coisa divergem (ex. `results_goal_reached_qty` vs `paid_traffic_revenue_realized`), **mostre os dois e sinalize**, não escolha um.
6. **Sem parser rígido de nomenclatura.** O padrão de nome de campanha varia por coordenação. Use `goal` (campaign_summary) + heurística de texto, nunca um regex fixo de `[V4][C:n]`.
7. **Avalie cada campanha pela métrica do SEU objetivo (`goal`).** NUNCA julgue uma campanha de engajamento/tráfego/awareness por CPL ou ROAS. Uma campanha de Visitas ao Perfil com 0 leads **não é fracasso** — avalie por custo por engajamento, reações, saves, video views, custo por seguidor. Ver tabela "Métricas por objetivo" em `references/fontes-mcp.md`. Só compare campanhas dentro do mesmo objetivo.
8. **Separar voz do cliente vs time V4.** Seção 7b = só cliente (verbatim). Seção 7c = conquistas V4 (verbatim do time na call ou fatos dos dados). Nunca misturar speakers.

## Passo 0 — Onboarding (quem é você + quais projetos)
1. A pessoa se identifica (nome/e-mail). Resolva o coordenador via `cockpit_list_coordinators` (match → `documentId`).
2. Liste **os projetos dela**: `cockpit_query_table` com `filterByUser=<documentId>` (ou `cockpit_list_projects`). Mostre a lista e peça para escolher **projeto(s)** + **período** (quarter, ex. Q2/2026, ou multi-quarter Q1+Q2).
3. Onboarding é em runtime via FLOW. Só é admissível cachear a config **do próprio usuário** (seu `documentId`), nunca base de clientes.

## Passo 1 — Resolver projeto e contexto (1 chamada)
`cockpit_query_table` com `search=<nome>` (ou já tendo o `documentId`) **e `resolveCalculations: true`** → o `healthScoreTable` traz quase todo o contexto. Em seguida `flow_project_data_list_connections` para saber os canais conectados (Meta/Google) e suas `capabilities`.

> **Busca:** ticker curto pode zerar — use trecho do nome do cliente ou `cockpit_get_project` com `documentId` do onboarding. Ver `references/operacao-runtime.md`.

Ver **`references/fontes-mcp.md`** para os campos exatos e as chamadas canônicas, **`references/pilares.md`** para o que cada pilar consome, e **`references/operacao-runtime.md`** para gotchas de runtime (parser NEKT, Ekyte, MCP no Cursor).

## Passo 2 — Período (quarter primeiro, granularização mensal)
A retrospectiva é do **QUARTER**, não do mês. Sempre:
1. Defina a janela do quarter (`startGte` / `endLt` exclusivo) — ex. Q2/2026 = abr–jun.
2. **Agregue por mês** dentro do quarter (abr, mai, jun…) e **concatene** numa leitura trimestral: totais do Q + evolução mês a mês (tendência, aceleração/desaceleração, sazonalidade).
3. Nas tabelas de investimento/resultado: **1 coluna por mês do quarter + coluna "Total Q"** à direita. A análise narrativa (seções 2, 4, 8) deve falar do **trimestre**; os meses são granularização, não o recorte principal.
4. Se o projeto entrou no meio do quarter (`projectStartDate`), marque meses anteriores como "—" e o período como parcial.
5. **Leitura da esquerda para a direita:** em qualquer comparativo **Projetado vs Realizado**, a ordem é sempre **Projetado (meta) → Realizado → Pacing/Δ%**. Nunca inverta (realizado antes de meta).
6. **Funil do quarter (seção 2):** fonte primária = planilha **Breakeven/Growthpack** (`paid_traffic_growthpack_updated_link`), não `paid_traffic_*` do cockpit (MTD). Rodar `node _fetch-breakeven-quarter.mjs {TICKER}` no piloto — export CSV público da planilha + aba **Funil de vendas** (projetado) + bloco **Investimento Meta** (realizado, soma abr+mai+jun). Ver `references/fontes-mcp.md` § J.

## Passo 3 — Coletar por pilar (paginando o NEKT)
Colete **só o que a fonte entrega** (ver Mapa de automação abaixo e `references/fontes-mcp.md`); o resto vira slot. Pagine o NEKT (limit 500, offset += 500) — os relatórios são granulares (ad×dia) e podem passar de 10k linhas/mês; agregue no consumidor por campanha/conjunto/criativo/mês.

**Parser:** linhas em `response.data.items` (não `rows`). Para engajamento (C:4, impulsionamento), faça chamada extra com `actionPresets: ["all"]` + `actionTypes` de engajamento.

**Divergência esperada:** leads NEKT (plataforma) vs `paid_traffic_leads_realized` (cockpit/funil) — mostrar os dois, não escolher um.

## Passo 4 — Analisar
Por pilar: rankings (melhores/piores), o que deu certo/errado, causa-raiz — **no nível do quarter**, citando evolução mensal quando relevante (ex. "CPL subiu de abr→jun"; "maio concentrou 60% das vendas"). Estruture aprendizados no formato **Start/Stop/Continue + A21** (ver `references/aprendizados-framework.md`) e derive os **Problemas por integrante** (mapeando cada achado ao papel responsável: tráfego→paid_media, criativo→designer/copy, funil→AM/CRM, gestão→PM/coord).

**E-commerce:** sempre apresentar **ROAS e CPA** juntos (compras, receita, investimento). **Inside Sales:** CPL + volume de leads. **Engajamento/tráfego:** métrica do `goal`, nunca CPL/ROAS.

## Passo 5 — Renderizar
Gere o HTML das **8 seções** seguindo **`references/template-output.md`** e a base **`assets/template-retrospectiva.html`**. HTML limpo (cola no Google Docs), proveniência por dado, slots amarelos onde falta fonte, cabeçalho de rastreabilidade.

## Passo 6 — Salvar
Salve em `./retrospectivas/[TICKER]-Q{n}-{ano}.html` no diretório de trabalho do coordenador (caminho configurável). Não dependa de pastas do Brain. (Centralização em repo Git = fase 2, fora do escopo.)

**Scripts opcionais (este repo):** pasta `scripts/` — `_fetch-mcp.mjs`, `_run-fetch.mjs`, `_fetch-breakeven-quarter.mjs`, `_build-html.py`.

## Mapa de automação (o que puxar sozinho vs slot)
- **✅ NEKT** (`flow_media_*`): investimento, impressões, cliques, CTR, CPC, CPM, alcance; **leads + CPL** (`actions.lead`); **e-commerce: vendas+receita+ROAS+CPA** (`actions.purchase`+`actionValues.purchase`); conversas (`conversations`); Page View (`landing_page_view`), Hook Rate (`video_view`/impr), Connect Rate (`landing_page_view`/`link_click`); copy/CTA (`creative_summary` `title`+`body`); goal/status/budget (`campaign_summary`).
- **✅ Cockpit** (`cockpit_query_table`, `resolveCalculations`): equipe, fee, flag, LT, fase, segmento, **modelo de negócio**, **CRM**, **critério MQL**; funil `paid_traffic_*`; resultado `results_*`; budget por canal; sentiment de call por vertical + `summary_reasoning`; WhatsApp sentiment; **CSAT/NPS** (`csat_*`); entregas `deliveries_*`.
- **🟡 Semi** (se preenchido/conectado): MQL/SQL/Vendas reais (cockpit digitado lá, ou `dados-kommo-audit`/`dados-activecampaign-audit`); Google performance (só com conexão NEKT — budget no cockpit ≠ dados); entregas detalhadas (`ekyte_list_tasks`).
- **🔴 Slot**: preview/imagem do criativo (creative_summary só traz texto); compra vs recompra; Soluções da matriz (por design).

## Regra de ouro de conversão (NEKT)
Conversão **não** está em `metrics` (`metrics.LEADS` não existe) — está em **`actions` / `costPerAction` / `actionValues`** de cada linha. Use `flow_media_conversion_summary`. Leads = `actions.lead` (não somar `lead_grouped`). E-commerce: ROAS = `SUM(actionValues.purchase)/SUM(COST)`, usar só `purchase` (não `omni_/web_in_store_/offsite_`). Cabeçalho obrigatório na saída: `projectDocumentId | platform | período | tool | provider=nekt`.
