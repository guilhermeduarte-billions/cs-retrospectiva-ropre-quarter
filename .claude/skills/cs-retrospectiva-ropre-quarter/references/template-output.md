# Contrato do output (HTML limpo, 8 seções)

Use `assets/template-retrospectiva.html` como esqueleto. Dados de referência do piloto Q2: `references/operacao-runtime.md`. Regras:

## Princípios de formatação
- **Cola no Google Docs**: tags semânticas (`h1/h2/h3`, `table`, `ul`), `<style>` simples no head, sem CSS pesado/flex/grid. Cores: vermelho V4 (`#e30613`) nos headers de seção.
- **Proveniência por dado**: sufixo `[NEKT]`, `[Cockpit]`, `[Ekyte]`, `[CRM]`, `[Call AAAA-MM-DD]`, `[WhatsApp]`.
- **Slot de fonte ausente**: bloco amarelo (`.slot`) "⚠ Preencher manualmente — fonte X não conectada".
- **Cabeçalho de rastreabilidade** (logo abaixo do título): `projectDocumentId | platform | período | tools | provider=nekt`. Marque se o período é **amostra** (não paginou tudo) ou **quarter fechado**.
- **Status colorido**: 🟢/🟡/🔴 ou classes `.ok`/`.bad`.
- **Leitura esquerda → direita**: em todo comparativo **Projetado (meta) vem antes de Realizado**. Ordem de colunas: `Projetado | Realizado | Pacing` (ou `Δ%`). Nunca `Realizado | Meta`.
- **Quarter, não mês**: o documento é retrospectiva do **trimestre**. Tabelas têm colunas mensais + **Total Q**; a narrativa sintetiza o quarter inteiro.

## As 8 seções (na ordem)
1. **Visão geral** — tabela: cliente/ticker, squad/coord, modelo de negócio + B2B/B2C, segmento, fee, plano de mídia (budget por canal), flag+HS, LT, CRM, critério MQL, **equipe** (todos os papéis do `projectTeam`).
2. **Resultado do quarter** — tabela resumo: meta alinhada, **Projetado (R$ ou qty) | Realizado | Pacing**. Fonte primária: **planilha Breakeven/Growthpack** (`paid_traffic_growthpack_updated_link`) → `node _fetch-breakeven-quarter.mjs {TICKER}` grava `_data/{TICKER}-breakeven-quarter.json`. **Inside Sales:** projetado = aba *Funil de vendas*; realizado = soma cols abr+mai+jun no bloco *Investimento Meta*; receita projetada = `results_goal_qty`. **E-commerce** sem aba Breakeven mensal: receita via `paid_traffic_revenue_*` / `results_goal_*` do cockpit. ⚠️ `paid_traffic_*` do cockpit = **mês corrente (MTD)** — só referência abaixo da tabela do quarter. Funil: Leads→MQL→SQL→Vendas→Receita (e-com pode ser só Receita).
3. **Investimentos e Resultados por canal** — **tabela mensal do quarter**: colunas `Abr/26 | Mai/26 | Jun/26 | Total Q` (adaptar meses ao quarter). Linhas: Investimento, Impressões, Cliques, CTR, CPM, CPC, Page View, Leads, Conversas, MQL, SQL, Vendas, Valor, **ROAS + CPA** (e-com), CPL/CPMQL/CP-SQL/CP-Venda (inside sales), Hook/Connect Rate. Um bloco por canal (Meta / Google). Após a tabela: parágrafo **"Síntese do quarter"** (tendência, melhor/pior mês, concentração de resultado). Slot p/ canal com budget mas sem conexão NEKT.
4. **O que deu certo / não deu certo** — separar por **objetivo (`goal`)**:
   - **Leads / Conversão (e-com)**: 6 blocos — ✅/❌ **campanhas**, ✅/❌ **conjuntos (públicos)**, ✅/❌ **anúncios** (top 5 cada). Nomes completos NEKT (`campaignName`, `groupName`, `adName`). Agregar `byCampaign`, `byAdset`, `byAd` no fetch.
   - **Engajamento / Tráfego / Awareness**: tabela própria com métrica do objetivo (custo/engajamento, reações, saves, video views, custo/seguidor, CPC, Connect Rate) — **nunca** CPL/ROAS.
   - Nota de leitura automática no **nível do quarter** (objetivo, fadiga, evolução entre meses).
5. **Criativo / Copy** — tabela criativo × (leads/compras, CPL/ROAS/CPA, formato) + copy vencedora (`body`). Slot para preview de imagem.
6. **Gestão de Projetos** — entregas Ekyte **visuais**:
   - **Resumo por tipo** (tabela: Tipo · Qtd · % do total) — extrair de tags no título (`[DE]`, `[CA]`, `[PC]`, `[CRM]`, `[AN]`, `[GT]`, …).
   - **Detalhe agrupado por tipo** (sub-header por tipo → tabela Data · Entrega), ou tabela única com coluna **Tipo** com cor.
   - SLA, demandas atrasadas, anomalias (cockpit). Não resumir só em "X tarefas".
7. **Cliente** — quatro blocos (ver `pilares.md` §4):
   - **7a. Síntese de sentimento (IA)** — neutra, evolução no quarter.
   - **7b. O que o CLIENTE disse** — verbatim **somente do cliente** (elogios | atenção), com speaker explícito.
   - **7c. Conquistas do quarter (time V4)** — verbatim **somente V4/Colli** na call **ou** vitórias objetivas dos dados (`[NEKT]`, `[Ekyte]`, `[Cockpit]`).
   - **7d. Apoio quantitativo** — scores, CSAT/NPS.
8. **Aprendizados & Ações — matriz por integrante** — um cabeçalho vermelho por pessoa (`projectTeam`), tabela `Problemas (auto) | Soluções/Ações (time)`. Problemas pré-preenchidos pelos dados do **quarter**; **Soluções = slot** "Ação proposta: ____".

## Período no header
- **Quarter fechado**: "Q2/2026 (abr–jun, paginado, mensal + total)".
- **Amostra parcial**: "Q2/2026 — amostra jun/2026 (abr–mai pendente paginação)" — deixar claro o que falta.
