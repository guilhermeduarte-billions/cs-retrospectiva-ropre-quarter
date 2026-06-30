# CHANGELOG — cs-retrospectiva-ropre-quarter

## [v1.3.0] — 2026-06-30
### Passo 7 — Publicar no Google Docs + registrar na planilha de Strategy Review
- **Passo 7 adicionado:** após salvar o HTML (Passo 6), a skill gera um `.docx` formatado via `python-docx` e faz upload para o Google Drive com `drive.files().update()` — o Google Doc existente tem seu conteúdo substituído sem alterar o link (mesmo `fileId`)
- **Por que .docx e não HTML direto:** upload de HTML via Drive MCP (`create_file` com `contentMimeType: text/html`) quebra tabelas, CSS e cores. A conversão .docx → Google Docs é fiel: tabelas com bordas, headers vermelhos V4 (`#E30613`), células amarelas para slots (`#FFF7D6`)
- **Script de referência:** `Brain/Trabalho V4/Projetos/retrospectiva-ropre-quarter/create_retro_docs_v2.py` — `RetroParser` (HTML→elementos) + `build_docx` (python-docx) + `upload_docx` (Drive API). Dict `PROJECTS = { TICKER: google_doc_id }` mapeia projeto → doc existente; novo projeto cria doc via Drive MCP primeiro
- **Passo 7b:** após upload, grava link na planilha de Strategy Review via Sheets API (`batchUpdate`): coluna U = `Retrospectiva AI` (link), coluna O = `Retrospectiva (By AI)` = TRUE. Config de spreadsheet é parâmetro (não-Brain); referência Billions: `1XURJFGB-We9Y3Uv-nbtJKn11mXqQtJ_btqujJ0NJPPc` aba `OFICIAL`
- **Credenciais:** `Brain/credentials/google_drive_token.json` (scope `drive` — suficiente para Drive + Sheets)
- **Validado** no piloto Q2/2026 (8 projetos: ASSO, LATI, SICA, CDGF, FIEE, SINQ, EZBU, TROPM) — todos upados e links gravados na planilha Billions

## [v1.2.3] — 2026-06-30
### Mídia = só NEKT (reverte a rota de API da v1.2.2)
- **Princípio 11:** todo dado de mídia vem do NEKT; proibido puxar de API de plataforma (`google-ads` MCP/GAQL, Meta direto). O que o NEKT não entregar vira **slot sinalizado para iteração** — o usuário decide. Flow instável = retry/slot, não gatilho de API
- Reverte a v1.2.2: removidas as rotas `keyword_view`/`search_term_view` via google-ads MCP da skill
- Keywords Google voltam a ser **só NEKT** (`flow_media_list_tables` + `flow_media_query resource:keyword_*`); ausência = slot p/ iteração
- Ajustado: `SKILL.md` (princípio 11, princípio 9, checklist Google, mapa de automação), `fontes-mcp.md` § F.1, `template-output.md` §4
- Decisão do Guilherme: "N quero puxar nada da API, apenas NEKT. O que n tiver me sinaliza que peço de iteração."

## [v1.2.2] — 2026-06-30
### Keywords + termos de busca Google via MCP google-ads (API direta)
- Rota primária de keywords agora é o **MCP `google-ads` (GAQL)** — `resource:keyword_view` (keywords) + `resource:search_term_view` (termos reais → descoberta de negativas). Mais confiável que o flow-proxy (que caiu com "Connection closed") e única fonte de search terms
- NEKT `flow_media_list_tables` + `keyword_*` rebaixado a fallback
- `search_term_view` canonizado como NÃO-PULÁVEL: classificar ICP / convertem / desperdício (DIY-produto) e recomendar **negativas** — revela vazamento que o nível de keyword esconde
- `SKILL.md`: Princípio 9 + checklist Google (Passo 3) + Mapa de automação com bloco google-ads MCP; custo em micros (÷1e6), customer_id sem hífens
- `fontes-mcp.md` § F.1 reescrito (Rota A API direta / Rota B NEKT fallback) + referência OUTMAT validada
- `template-output.md` §4: bloco Google com keywords + termos + caixa de ação de negativas
- Validado no OUTMAT Q2/2026: R$ 870,10 / 12 conv (bate GrowthPack); melhor keyword "projeto automação residencial" CPL R$ 26; ~R$ 90 em termos DIY a negativar

## [v1.2.1] — 2026-06-29
### Fallback de descoberta do GrowthPack pelo FLOW
- Sem planilha-mestra do squad configurada, o link do GrowthPack vem do cockpit: campo **`paid_traffic_growthpack_updated_link`** (toda linha de projeto no FLOW tem)
- Ordem de prioridade canonizada: 1) planilha-mestra → 2) `paid_traffic_growthpack_updated_link` do FLOW → 3) slot (só se ambos vazios)
- `SKILL.md`: Passo 0 com ordem de prioridade explícita + Princípio 10 atualizado
- `fontes-mcp.md`: § B (campo na tabela de contexto) + § J.0 (fallback detalhado)

## [v1.2.0] — 2026-06-29
### GrowthPack como Realizado consolidado do quarter + fluxo macro→micro
- **Espinha macro→micro:** análise abre pelo GrowthPack (Projetado vs Realizado do quarter + split por canal) e só então desce ao micro NEKT (campanha→conjunto→anúncio→keyword). O Realizado consolidado do quarter **não existe no FLOW** (cockpit é MTD) — mora no GrowthPack
- **Princípio 10:** GrowthPack = fonte de verdade do Realizado; descoberta via planilha-mestra do squad (índice configurável, agnóstico ao Brain) → `Link do GrowthPack` do projeto
- **Passo 0:** onboarding agora cruza FLOW + planilha-mestra (filtra `Coordenacao` → projetos + links de GrowthPack)
- **Passo 2 item 6** reescrito: aba "Acompanhamento Mensal" (gid padrão 1422566774), ancoragem do quarter por `Data inicial/final` (linha `Ano` mislabela 2026), mapa de linhas consolidadas + blocos por canal
- **Passo 4** reordenado: macro (GrowthPack) → por canal → reconciliação NEKT×GrowthPack → micro (NEKT)
- **Nova ref `growthpack-acesso.md`:** 3 vias de acesso ao Sheets (conector Google Drive MCP · export CSV público · service account Google Cloud com passo a passo) — ensina o time a criar acesso; agnóstico ao Brain
- **`fontes-mcp.md` § J** reescrito: planilha-mestra (J.0) + aba Acompanhamento Mensal com mapa de linhas (J.1) + reconciliação obrigatória (J.2) + gotchas (J.3); referência EEAA Q2/2026 validada
- **`template-output.md`:** seção 2 macro (Big Numbers + Projetado vs Realizado + evolução mensal + Q-1 vs Q) · seção 3 split por canal + reconciliação · seção 4 **vencedores detalhados** iterados (campanhas/conjuntos/criativos/keywords com Status + Critério de leitura, bloco awareness separado)
- **`pilares.md` §1** agora explicita macro (GrowthPack) → reconciliação → micro (NEKT)

## [v1.1.5] — 2026-06-29
### Toda a cadeia de ranking é NÃO-PULÁVEL (campanha → conjunto → anúncio)
- Princípio 9 expandido: não só públicos e keywords — TODOS os 3 níveis são obrigatórios; slot só aceito quando tool confirmar ausência
- Checklist Passo 3: cada item marcado **OBRIGATÓRIO** explicitamente; regra de slot restrita
- `pilares.md` §1 e `template-output.md` §4: marcação NÃO-PULÁVEL nos 3 níveis (campanhas, conjuntos, anúncios) para Meta e Google

## [v1.1.4] — 2026-06-29
### Públicos (Meta) e keywords (Google) canonizados como NÃO-PULÁVEIS
- Princípio 9 adicionado: `flow_media_group_summary` por campanha (públicos Meta) e `flow_media_list_tables` + `flow_media_query resource:keyword_*` (keywords Google Search) são obrigatórios — nunca slot sem tentar
- `SKILL.md`: checklist obrigatório de coleta no Passo 3 (Meta Ads + Google Ads em 5 passos cada); Mapa de automação atualizado
- `pilares.md` §1: ranking em 3 níveis explicitado; note NÃO-PULÁVEL em conjuntos/públicos e keywords; instrução F.1 para keywords
- `fontes-mcp.md`: seção F.1 adicionada (fluxo `list_tables` → `flow_media_query resource:keyword_*`; gotcha custo micros; exemplo OTMT Q2 slot com motivo)
- `template-output.md` §4: blocos Meta e Google Search com marcação NÃO-PULÁVEL explícita
- Referência: OTMT Q2/2026 — públicos ausentes por gap de coleta (raiz desta versão)

## [v1.1.3] — 2026-06-26
### Funil do quarter via Growthpack (CSV)
- `_fetch-breakeven-quarter.mjs`: export CSV público (sem gws) + parser automático
- Inside Sales: projetado (aba Funil de vendas) + realizado (soma Investimento Meta abr–jun)
- E-commerce sem aba Breakeven: fallback receita cockpit
- `parseNum` corrigido para decimal API vs formato BR
- TROPM Q2: funil preenchido no HTML; UMBRO: receita 95,9% pacing
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
### Piloto Q2 real (TROPM + UMBRO)
- Run end-to-end via MCP: quarter paginado abr–jun, HTML gerado com dados reais
- `references/operacao-runtime.md`: gotchas parser NEKT (`data.items`), busca cockpit, Ekyte, MCP Cursor
- Layout: Projetado → Realizado (esq→dir); tabela mensal + Total Q; ROAS+CPA e-commerce
- Engajamento C:4 avaliado por custo/engajamento (chamada extra actionTypes)
- Divergência NEKT leads vs cockpit funil documentada e renderizada
- Scripts piloto: `_fetch-mcp.mjs`, `_run-fetch.mjs`, `_build-html.py`
- Outputs: `retrospectivas/TROPM-Q2-2026.html`, `UMBRO-Q2-2026.html`

## [v1.0.0] — 2026-04-14
- Versão inicial com 8 seções, pilares, template HTML, protótipos
