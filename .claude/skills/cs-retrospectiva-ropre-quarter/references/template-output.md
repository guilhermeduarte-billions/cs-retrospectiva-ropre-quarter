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
2. **Resultado do quarter (MACRO — GrowthPack)** — abre com **Big Numbers** (cards): Meta de leads Q · Leads realizados Q · Atingimento % · Gap · Investimento projetado · Investimento realizado · CPL realizado · CPL projetado. Depois a tabela **Projetado vs Realizado**: `Indicador | Projetado | Realizado | Δ abs | Δ % | Motivo provável`. Fonte primária = **GrowthPack, aba "Acompanhamento Mensal"** (ver `fontes-mcp.md` § J): projetado = linhas `Meta`/`Plano de mídia Mês`; realizado = linhas `Leads`/`Investimento`, somando as 3 colunas do quarter. **MQL/SQL/Vendas/Receita** = linhas `(manual)` da planilha; quase sempre "-" → slot (não inventar). ⚠️ `paid_traffic_*` do cockpit = **MTD**, NUNCA usar como Realizado do quarter. **Evolução mensal** (sub-tabela): `Mês | Invest planejado | Invest realizado | Meta leads | Leads realizados | Atingimento | CPL | Diagnóstico` — identifica o mês de gap e o de recuperação. Se houver dados do quarter anterior na mesma planilha, adicione **comparativo Q-1 vs Q** (invest, meta, leads, atingimento, CPL).
3. **Investimentos e Resultados por canal (MACRO + RECONCILIAÇÃO)** — **3a. Split por canal (GrowthPack):** `Canal | Investimento Q | Leads/conversões Q | CPL | % do investimento | % dos leads | Diagnóstico` (blocos *Investimento Meta* e *Investimento Google* da aba). **3b. Reconciliação NEKT vs GrowthPack (obrigatória):** `Métrica | GrowthPack | NEKT paginado | Diferença | Leitura` para investimento e leads de cada canal — diferença pequena = data de corte; GrowthPack é a base oficial. **3c. Evolução mensal por canal (NEKT, micro):** tabela mensal `Abr | Mai | Jun | Total Q` com Investimento, Impressões, Cliques, CTR, CPM, CPC, Page View, Leads, Conversas, **ROAS+CPA** (e-com), CPL, Hook/Connect Rate. Após: parágrafo **"Síntese do quarter"** (tendência, melhor/pior mês). Slot p/ canal com budget mas sem conexão NEKT.
4. **O que deu certo / não deu certo + Vencedores (MICRO — NEKT)** — separar por **objetivo (`goal`)**:
   - **Leads / Conversão (e-com)**: todos os 3 níveis são NÃO-PULÁVEIS em ambos os canais. Slot só se a tool confirmar ausência:
     - Meta: ✅/❌ **campanhas (NÃO-PULÁVEL)** · ✅/❌ **conjuntos/públicos (NÃO-PULÁVEL — `flow_media_group_summary`)** · ✅/❌ **anúncios (NÃO-PULÁVEL — `flow_media_ad_summary`)** (top 5 cada). Nomes completos NEKT (`campaignName`, `groupName`, `adName`).
     - Google Search: ✅/❌ **campanhas (NÃO-PULÁVEL)** · ✅/❌ **ad groups (NÃO-PULÁVEL)** · ✅/❌ **anúncios (NÃO-PULÁVEL)** · ✅/❌ **keywords (NÃO-PULÁVEL — só NEKT: `flow_media_list_tables` + `flow_media_query resource:keyword_*`)** (top 10). Se o NEKT não tiver keyword data (sem recurso ou flow falhou), **slot sinalizado para iteração** — nunca usar API de plataforma (ver `fontes-mcp.md` § F.1 e princípio 11).
   - **Engajamento / Tráfego / Awareness**: tabela própria com métrica do objetivo (custo/engajamento, reações, saves, video views, custo/seguidor, CPC, Connect Rate) — **nunca** CPL/ROAS.
   - Nota de leitura automática no **nível do quarter** (objetivo, fadiga, evolução entre meses).
   - **Vencedores detalhados (formato canônico — iterar sempre):**
     - **Melhores campanhas** (uma sub-tabela por canal): `Campanha (nome completo NEKT) | Status (ACTIVE/PAUSED/ENABLED) | Investimento | Leads/Conversões | CPL | Critério de leitura | Fonte`. A coluna **Critério de leitura** explicita o objetivo da comparação ("Ranqueada dentro de OUTCOME_LEADS; não comparada com awareness") — evita comparar maçã com laranja.
     - **Melhores conjuntos/públicos** (Meta) e **ad groups** (Google): `Conjunto/Público (groupName) | Campanha | Investimento | Leads | CPL`.
     - **Melhores criativos**: `Criativo/anúncio (adName) | Campanha | Investimento | Leads | CPL | Leitura`. Leitura distingue **vencedor por volume** (muitos leads) de **bom sinal/baixo volume** (CPL ótimo mas pouco volume — precisa validar). Incluir a copy vencedora (`creative_summary.body`).
     - **Melhores keywords** (Google Search): `Keyword | Cliques | Conversões | CPL/CPC | Leitura`.
     - **Awareness/Engajamento** (bloco separado): `Canal | Campanha | Investimento | Métrica compatível (impressões/CPM/video views) | Leitura` — marcar explicitamente "Não avaliar por CPL/ROAS porque o objetivo é awareness".
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
