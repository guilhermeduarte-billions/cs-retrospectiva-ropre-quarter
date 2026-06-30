---
name: cs-retrospectiva-ropre-quarter
description: Gera automaticamente a retrospectiva de Growth Marketing do Quarter de um cliente para as reuniões de ROPRE, cruzando FLOW/NEKT (mídia + conversões Meta/Google), cockpit (contexto, funil, resultado, sentiment, CSAT/NPS, entregas), Ekyte e BigQuery, num HTML com 8 seções por pilar (Tráfego, Criativo/Copy, Gestão de Projetos, Cliente, CRM/Funil) e uma matriz Problemas|Soluções por integrante. Publica automaticamente no Google Docs (python-docx + Drive API) e registra o link na planilha de Strategy Review. É agnóstica a coordenação/gerência: a pessoa faz onboarding (se identifica → a skill descobre os projetos dela no FLOW e na planilha-mestra de GrowthPacks do squad) e roda a retro dos seus projetos. Análise macro→micro: o Realizado consolidado do quarter vem do GrowthPack (Google Sheets, não existe no FLOW); o NEKT estratifica o micro (campanha→conjunto→anúncio→keyword). ZERO base local — FLOW/Ekyte/BigQuery via MCP + GrowthPack via Sheets. Use quando o usuário rodar /cs-retrospectiva-ropre-quarter, pedir pra "fazer a retrospectiva do quarter do cliente X", "montar a retro do ROPRE", "o que deu certo e errado no trimestre", "retrospectiva de growth do cliente", ou preparar o insumo de dados de uma reunião de ROPRE/retrospectiva trimestral.
author: guilhermeduarte-billions
version: 1.3.0
---

# cs-retrospectiva-ropre-quarter — Retrospectiva de Growth do Quarter (ROPRE)

Dado um **coordenador**, um **projeto** e um **período (quarter)**, gera um **HTML de retrospectiva** com o que deu certo / o que deu errado / aprendizados por pilar, pronto para a reunião de ROPRE e para colar num Google Docs. A skill **municia a reunião, não decide**: ela traz os dados e os Problemas; as **Soluções/Ações ficam em branco** para o time preencher.

Não confundir com `analise-ropre-quarter` (que **avalia** um ROPRE pronto por rubrica). Esta **gera** o conteúdo a partir de dados reais.

## Fluxo macro → micro (espinha da análise)
A retrospectiva desce do consolidado para o granular, nesta ordem:
1. **MACRO (GrowthPack):** Projetado vs Realizado **do quarter inteiro** — leads, investimento, CPL, CTR, taxa de conversão. **O Realizado consolidado do quarter NÃO existe no FLOW** (cockpit é MTD); ele mora no **GrowthPack** do projeto (aba "Acompanhamento Mensal").
2. **POR CANAL (GrowthPack):** split Meta Ads vs Google Ads (investimento, leads, CPL por canal) — blocos "Investimento Meta" e "Investimento Google" da mesma aba.
3. **MICRO (NEKT):** estratificação campanha → conjunto/público → anúncio → keyword, via integração NEKT. Aqui entram os rankings e os vencedores detalhados.
4. **RECONCILIAÇÃO:** tabela NEKT vs GrowthPack (investimento e leads por canal) — diferenças pequenas são esperadas (data de corte); **GrowthPack é a base oficial**, NEKT é o detalhe.

O GrowthPack é a **fonte de verdade do Realizado**; o NEKT explica *por quê* (quais campanhas/públicos/criativos puxaram o número).

## Princípios inegociáveis
1. **ZERO base local.** Nenhum dado vem de arquivos do Brain (`projetos.yaml`, `Clientes/`, relatórios). As fontes são **MCP** (FLOW cockpit/media, Ekyte, BigQuery) **+ GrowthPack** (Google Sheets do squad, lido via Drive MCP / CSV público / service account — `references/growthpack-acesso.md`). Tudo externo e configurável; nada de path pessoal. A skill roda para **qualquer coordenação/gerência**.
2. **Proveniência sempre.** Todo dado carrega a fonte entre colchetes — `[NEKT]`, `[Cockpit]`, `[Ekyte]`, `[CRM]`, `[Call AAAA-MM-DD]`, `[WhatsApp]`.
3. **Anti-blefe → slot.** Lacuna nunca vira invenção. Onde falta fonte, renderize um **slot** visível ("⚠ Preencher manualmente — fonte X não conectada"). Nunca deduza número.
4. **Ações são do time.** A skill pré-preenche **Problemas** (a partir dos dados); a coluna **Soluções/Ações fica vazia** (slot) — o time preenche na reunião.
5. **Sinalize divergências.** Se dois campos do FLOW para a mesma coisa divergem (ex. `results_goal_reached_qty` vs `paid_traffic_revenue_realized`), **mostre os dois e sinalize**, não escolha um.
6. **Sem parser rígido de nomenclatura.** O padrão de nome de campanha varia por coordenação. Use `goal` (campaign_summary) + heurística de texto, nunca um regex fixo de `[V4][C:n]`.
7. **Avalie cada campanha pela métrica do SEU objetivo (`goal`).** NUNCA julgue uma campanha de engajamento/tráfego/awareness por CPL ou ROAS. Uma campanha de Visitas ao Perfil com 0 leads **não é fracasso** — avalie por custo por engajamento, reações, saves, video views, custo por seguidor. Ver tabela "Métricas por objetivo" em `references/fontes-mcp.md`. Só compare campanhas dentro do mesmo objetivo.
8. **Separar voz do cliente vs time V4.** Seção 7b = só cliente (verbatim). Seção 7c = conquistas V4 (verbatim do time na call ou fatos dos dados). Nunca misturar speakers.
9. **Toda a cadeia de ranking é NÃO-PULÁVEL.** Nenhum nível pode ser omitido sem tentativa real. Os três níveis obrigatórios são:
   - **Campanhas** (`flow_media_campaign_summary` + `flow_media_conversion_summary`) — sempre.
   - **Conjuntos / Públicos** (`flow_media_group_summary` por campanha) — sempre. Para Meta: nome do público em `groupName`. Para Google: ad groups.
   - **Anúncios** (`flow_media_ad_summary`) — sempre.
   - **Keywords Google Ads Search** — **só NEKT**: `flow_media_list_tables` (`platform: google_ads`) → se houver recurso `keyword_*`, `flow_media_query resource:keyword_*`. Ver `references/fontes-mcp.md` § F.1. Se o NEKT não retornar (sem recurso, ou flow instável), **slot sinalizado para iteração** — **não** usar API de plataforma (princípio 11).
   Slot NUNCA substitui ausência de esforço no NEKT. Slot é aceito quando o NEKT confirma ausência do dado, OU quando o NEKT falha e o dado fica pendente de iteração (nunca contornar por API).
10. **GrowthPack = Realizado consolidado do quarter (não está no FLOW).** O macro vem da planilha, não do cockpit (MTD). Sempre começar pelo GrowthPack (Projetado vs Realizado do quarter + split por canal) e só então descer ao micro NEKT. A descoberta do GrowthPack é via **planilha-mestra do squad** (índice configurável, não-Brain) → `Link do GrowthPack` do projeto; **fallback: o próprio FLOW tem o link** no campo `paid_traffic_growthpack_updated_link` do cockpit (use quando não houver planilha-mestra configurada). Acesso à planilha: conector Google Drive (MCP), export CSV público ou service account Google Cloud — ver `references/growthpack-acesso.md`. A skill é **agnóstica ao Brain**: nada de ingest local; qualquer pessoa do time configura o link do seu squad e roda.
11. **Mídia = SÓ NEKT. Nunca puxar de API de plataforma.** Todo dado de mídia (campanhas, conjuntos, anúncios, keywords) vem do **NEKT** (`flow_media_*`). É proibido contornar pela API direta da plataforma (`google-ads` MCP/GAQL, Meta direto) — o NEKT é o pipeline sancionado e reproduzível pro time todo. **O que o NEKT não entregar vira slot sinalizado** ("⚠ pendente — NEKT não retornou; sinalizar para iteração"), e o usuário decide se itera. Se o flow-proxy falhar (ex. "Connection closed"), é retry/slot do NEKT — **não** é gatilho para usar API.

## Passo 0 — Onboarding (quem é você + quais projetos)
1. A pessoa se identifica (nome/e-mail). Resolva o coordenador via `cockpit_list_coordinators` (match → `documentId`).
2. Liste **os projetos dela** por **duas vias complementares**:
   - **FLOW:** `cockpit_query_table` com `filterByUser=<documentId>` (ou `cockpit_list_projects`).
   - **Planilha-mestra do squad (GrowthPacks):** índice configurável por squad. Filtra `Coordenacao = <nome do usuário>` → cada linha traz `Projeto` + `Link do GrowthPack` (+ HS, Flag, Score Ops, FEE, Mídia). É daqui que sai o link do GrowthPack de cada projeto para o Passo 2. Ver `references/fontes-mcp.md` § J e `references/growthpack-acesso.md`.
   Mostre a lista e peça para escolher **projeto(s)** + **período** (quarter, ex. Q2/2026, ou multi-quarter Q1+Q2).

   **Descoberta do link do GrowthPack — ordem de prioridade:**
   1. **Planilha-mestra do squad** (coluna `Link do GrowthPack`) — via primária quando configurada.
   2. **FLOW (fallback):** se não houver planilha-mestra configurada (ou o projeto não estiver nela), pegue o link direto do cockpit: campo **`paid_traffic_growthpack_updated_link`** (`cockpit_query_table` com `resolveCalculations: true`). Toda linha de projeto no FLOW tem esse campo. Daí em diante o fluxo do Passo 2 é idêntico (abrir a aba "Acompanhamento Mensal").
   3. Só vira slot se **nem a mestra nem o FLOW** tiverem link — aí registre "⚠ GrowthPack não localizado (sem planilha-mestra e campo do FLOW vazio)".
3. Onboarding é em runtime. Só é admissível cachear a config **do próprio usuário** (seu `documentId` + a **URL da planilha-mestra do seu squad**), nunca base de clientes. A skill é **agnóstica ao Brain**: o link do squad é um parâmetro de config, não um caminho local.

## Passo 1 — Resolver projeto e contexto (1 chamada)
`cockpit_query_table` com `search=<nome>` (ou já tendo o `documentId`) **e `resolveCalculations: true`** → o `healthScoreTable` traz quase todo o contexto. Em seguida `flow_project_data_list_connections` para saber os canais conectados (Meta/Google) e suas `capabilities`.

> **Busca:** ticker curto (`TROPM`) pode zerar — use trecho do nome (`Tropical`) ou `cockpit_get_project` com `documentId` do onboarding. Ver `references/operacao-runtime.md`.

Ver **`references/fontes-mcp.md`** para os campos exatos e as chamadas canônicas, **`references/pilares.md`** para o que cada pilar consome, e **`references/operacao-runtime.md`** para gotchas de runtime (parser NEKT, Ekyte, MCP no Cursor).

## Passo 2 — Período (quarter primeiro, granularização mensal)
A retrospectiva é do **QUARTER**, não do mês. Sempre:
1. Defina a janela do quarter (`startGte` / `endLt` exclusivo) — ex. Q2/2026 = abr–jun.
2. **Agregue por mês** dentro do quarter (abr, mai, jun…) e **concatene** numa leitura trimestral: totais do Q + evolução mês a mês (tendência, aceleração/desaceleração, sazonalidade).
3. Nas tabelas de investimento/resultado: **1 coluna por mês do quarter + coluna "Total Q"** à direita. A análise narrativa (seções 2, 4, 8) deve falar do **trimestre**; os meses são granularização, não o recorte principal.
4. Se o projeto entrou no meio do quarter (`projectStartDate`), marque meses anteriores como "—" e o período como parcial.
5. **Leitura da esquerda para a direita:** em qualquer comparativo **Projetado vs Realizado**, a ordem é sempre **Projetado (meta) → Realizado → Pacing/Δ%**. Nunca inverta (realizado antes de meta).
6. **Macro do quarter (Projetado vs Realizado) = GrowthPack, não FLOW.** O Realizado consolidado do quarter **não existe no cockpit** (campos `paid_traffic_*` são MTD). Fonte primária = **GrowthPack do projeto**, aba **"Acompanhamento Mensal"** (gid padrão `1422566774` no template GrowthPack 3.0 — confirmar pelo nome da aba, o gid pode variar). Lá os meses são colunas; ancore o quarter pelas linhas `Data inicial`/`Data final`/`Mês` (a linha `Ano` mislabela alguns 2026 — não confie nela). Leia as linhas consolidadas:
   - **Meta** (leads projetado/mês) · **Leads** (realizado/mês) · **% da Meta** (atingimento).
   - **Plano de mídia Mês** (invest. projetado) · **Investimento** (invest. realizado).
   - **CTR**, **Taxa de Conversão**, **Custo por Lead**.
   - **Por canal:** bloco **"Investimento Meta"** (On-Facebook Leads + Website Leads, invest, CPL) e bloco **"Investimento Google"** (Leads, invest, CPL).
   Some abr+mai+jun para o Total Q. Marque junho como **parcial** se a data de corte for antes do fim do mês. Ver `references/fontes-mcp.md` § J. (`paid_traffic_growthpack_updated_link` do cockpit é um fallback para achar o link; a via primária é a planilha-mestra do Passo 0.)

## Passo 3 — Coletar por pilar (paginando o NEKT)
Colete **só o que a fonte entrega** (ver Mapa de automação abaixo e `references/fontes-mcp.md`); o resto vira slot. Pagine o NEKT (limit 500, offset += 500) — os relatórios são granulares (ad×dia) e podem passar de 10k linhas/mês; agregue no consumidor por campanha/conjunto/criativo/mês.

**Parser:** linhas em `response.data.items` (não `rows`). Para engajamento (C:4, impulsionamento), faça chamada extra com `actionPresets: ["all"]` + `actionTypes` de engajamento.

**Divergência esperada:** leads NEKT (plataforma) vs `paid_traffic_leads_realized` (cockpit/funil) — mostrar os dois, não escolher um.

### Checklist obrigatório de coleta — NENHUM nível é opcional

> **Regra:** slot só é aceito quando a tool confirma que o dado não existe. Ausência de esforço não é slot — é erro de execução.

**Meta Ads — por cada campanha ativa no quarter:**
1. **`flow_media_conversion_summary`** por mês (abr/mai/jun) → totais por campanha — **OBRIGATÓRIO**
2. **`flow_media_group_summary`** por campanha → ranking de conjuntos/públicos (top 5 ✅, bottom 5 ❌) — **OBRIGATÓRIO, NUNCA slot sem tentar**
3. **`flow_media_ad_summary`** → ranking de anúncios (top 5 ✅, bottom 5 ❌ por leads/CPA) — **OBRIGATÓRIO**

**Google Ads — por cada campanha Search/Display ativa no quarter:**
1. **`flow_media_conversion_summary`** por mês → totais — **OBRIGATÓRIO**
2. **`flow_media_group_summary`** → ranking de ad groups — **OBRIGATÓRIO**
3. **`flow_media_ad_summary`** → ranking de anúncios — **OBRIGATÓRIO**
4. **`flow_media_list_tables`** (`platform: google_ads`) → verificar se há recurso `keyword_*` — **OBRIGATÓRIO (só NEKT)**
5. Se houver: **`flow_media_query resource:keyword_*`** → ranking top 10 keywords por CPL/CPC — **OBRIGATÓRIO**
6. Se o NEKT não tiver recurso de keyword, ou o flow falhar: **slot sinalizado para iteração** — **NÃO** usar API de plataforma (princípio 11). Custo Google em **micros** (÷ 1.000.000).

## Passo 4 — Analisar (macro → micro)
Siga a espinha: **GrowthPack primeiro (macro + por canal), NEKT depois (micro)**.
1. **Macro (GrowthPack):** Projetado vs Realizado do quarter (leads, investimento, CPL, atingimento). Diagnóstico central: bateu/não bateu a meta e por quê (qual mês puxou pra baixo, CPL subiu/caiu).
2. **Por canal (GrowthPack):** participação de Meta vs Google no investimento e nos leads; qual canal foi mais eficiente.
3. **Reconciliação NEKT vs GrowthPack:** tabela com investimento e leads por canal nas duas fontes; sinalizar diferenças (data de corte é a causa comum). **GrowthPack é a base oficial.**
4. **Micro (NEKT):** rankings (melhores/piores) campanha → conjunto/público → anúncio → keyword, **no nível do quarter**, citando evolução mensal quando relevante (ex. "CPL subiu de abr→jun"). **Avalie cada campanha pela métrica do seu `goal`** (não comparar leads com awareness).

Estruture aprendizados no formato **Start/Stop/Continue + A21** (ver `references/aprendizados-framework.md`) e derive os **Problemas por integrante** (tráfego→paid_media, criativo→designer/copy, funil→AM/CRM, gestão→PM/coord).

**E-commerce:** sempre apresentar **ROAS e CPA** juntos (compras, receita, investimento). **Inside Sales:** CPL + volume de leads. **Engajamento/tráfego:** métrica do `goal`, nunca CPL/ROAS.

## Passo 5 — Renderizar
Gere o HTML das **8 seções** seguindo **`references/template-output.md`** e a base **`assets/template-retrospectiva.html`**. HTML limpo (cola no Google Docs), proveniência por dado, slots amarelos onde falta fonte, cabeçalho de rastreabilidade.

## Passo 6 — Salvar
Salve em `./retrospectivas/[TICKER]-Q{n}-{ano}.html` no diretório de trabalho do coordenador (caminho configurável). Não dependa de pastas do Brain. (Centralização em repo Git = fase 2, fora do escopo.)

**Piloto de referência:** `Brain/Trabalho V4/Projetos/retrospectiva-ropre-quarter/` (`_fetch-mcp.mjs`, `_run-fetch.mjs`, `_fetch-breakeven-quarter.mjs`, `_build-html.py`, `retrospectivas/*.html`).

## Passo 7 — Publicar no Google Docs

Após salvar o HTML (Passo 6), gere um `.docx` formatado e publique no Google Drive. O documento substituído **mantém o mesmo link** — só o conteúdo é trocado. Em seguida registre o link na planilha de Strategy Review.

### 7a. Gerar .docx e fazer upload

Use o stack Python do ingest Brain (`Brain/automations/meet_transcripts/.venv/`, Python 3.9, `python-docx 1.2.0` + `google-api-python-client`):

```bash
cd /Users/guiduarte/Brain/automations/meet_transcripts
.venv/bin/python3 "../../Trabalho V4/Projetos/retrospectiva-ropre-quarter/create_retro_docs_v2.py"
```

O script `create_retro_docs_v2.py` (em `Brain/Trabalho V4/Projetos/retrospectiva-ropre-quarter/`):
1. Lê cada `retrospectivas/[TICKER]-Q{n}-{ano}.html` e parseia com `RetroParser` (state-machine)
2. Gera `.docx` via `python-docx`: headers H2 em vermelho V4 (`#E30613`) fundo branco, H3 vermelho uppercase, tabelas com bordas cinza e cabeçalho `#F2F2F2`, células de slot com fundo amarelo `#FFF7D6`
3. Faz upload via `drive.files().update(fileId=<doc_id>, media_body=<docx_bytes>, mimetype=application/vnd.openxmlformats-officedocument.wordprocessingml.document)` — Drive converte .docx para Google Docs nativo, preservando tabelas e formatação

**Credenciais:** `Brain/credentials/google_drive_token.json` (scope `drive` — suficiente para upload)

**Mapeamento de Google Doc IDs** — o script mantém um dict `PROJECTS = { "TICKER": "google_doc_id" }`. Para **novo projeto** (sem Google Doc existente):
1. Crie o doc via `mcp__claude_ai_Google_Drive__create_file` com `mimeType: "application/vnd.google-apps.document"` e título `Retrospectiva [TICKER] Q{n}/{ano}`
2. Anote o `fileId` retornado e adicione ao dict `PROJECTS` no script

### 7b. Registrar na planilha de Strategy Review

Após o upload, grave o link do Google Doc na planilha-mestra do squad:

**Billions (Squad Guilherme Duarte):**
- Spreadsheet: `1XURJFGB-We9Y3Uv-nbtJKn11mXqQtJ_btqujJ0NJPPc`, aba `OFICIAL` (gid `891648798`)
- Coluna U = `Retrospectiva AI` → link `https://docs.google.com/document/d/<doc_id>/edit`
- Coluna O = `Retrospectiva (By AI)` → booleano `TRUE`
- Identificar a linha do projeto por `Coordenacao = "Guilherme Duarte"` + match de nome/ticker

Use Sheets API com as mesmas credenciais Drive:
```python
sheets = build("sheets", "v4", credentials=creds)
sheets.spreadsheets().values().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={"valueInputOption": "RAW", "data": [
        {"range": f"OFICIAL!U{row}", "values": [[link]]},
        {"range": f"OFICIAL!O{row}", "values": [[True]]},
    ]}
).execute()
```

Para outros squads, ajuste o `SHEET_ID` e o nome da aba conforme a planilha-mestra do squad. A skill é agnóstica; o spreadsheetId é um parâmetro de config — não depende do Brain.

### 7c. Output do Passo 7

Ao concluir, exiba para cada projeto:
```
TICKER  parse(N elem)  docx(XKB)  ✅  https://docs.google.com/document/d/<id>/edit
```
E ao final: confirmação de que os links foram gravados na planilha + número de linhas atualizadas.

## Mapa de automação (o que puxar sozinho vs slot)
- **✅ GrowthPack** (planilha-mestra do squad → `Link do GrowthPack` → aba "Acompanhamento Mensal"): **Realizado consolidado do quarter** (não existe no FLOW) — leads projetado/realizado, % da meta, investimento projetado/realizado, CTR, taxa de conversão, CPL; **split por canal** (blocos Investimento Meta / Investimento Google). É o **macro** que abre a análise. Acesso: Drive MCP / CSV público / service account (ver `references/growthpack-acesso.md`).
- **✅ NEKT** (`flow_media_*`): **micro** — investimento, impressões, cliques, CTR, CPC, CPM, alcance; **leads + CPL** (`actions.lead`); **e-commerce: vendas+receita+ROAS+CPA** (`actions.purchase`+`actionValues.purchase`); conversas (`conversations`); Page View (`landing_page_view`), Hook Rate (`video_view`/impr), Connect Rate (`landing_page_view`/`link_click`); copy/CTA (`creative_summary` `title`+`body`); goal/status/budget (`campaign_summary`); **públicos/conjuntos Meta** (`group_summary` por campanha — NÃO slot); **keywords Google Ads** (só NEKT: `flow_media_list_tables` + `flow_media_query resource:keyword_*` — NÃO slot sem verificar; se NEKT não tiver, slot p/ iteração, **nunca API**). Usar também para **reconciliar** investimento/leads por canal contra o GrowthPack.
- **🔴 NÃO usar** (princípio 11): API direta de plataforma (`google-ads` MCP/GAQL, Meta direto). Mídia = só NEKT. Lacuna do NEKT = slot sinalizado para iteração.
- **✅ Cockpit** (`cockpit_query_table`, `resolveCalculations`): equipe, fee, flag, LT, fase, segmento, **modelo de negócio**, **CRM**, **critério MQL**; funil `paid_traffic_*`; resultado `results_*`; budget por canal; sentiment de call por vertical + `summary_reasoning`; WhatsApp sentiment; **CSAT/NPS** (`csat_*`); entregas `deliveries_*`.
- **🟡 Semi** (se preenchido/conectado): MQL/SQL/Vendas reais (cockpit digitado lá, ou `dados-kommo-audit`/`dados-activecampaign-audit`); Google performance (só com conexão NEKT — budget no cockpit ≠ dados); entregas detalhadas (`ekyte_list_tasks`).
- **🔴 Slot**: preview/imagem do criativo (creative_summary só traz texto); compra vs recompra; Soluções da matriz (por design).

## Regra de ouro de conversão (NEKT)
Conversão **não** está em `metrics` (`metrics.LEADS` não existe) — está em **`actions` / `costPerAction` / `actionValues`** de cada linha. Use `flow_media_conversion_summary`. Leads = `actions.lead` (não somar `lead_grouped`). E-commerce: ROAS = `SUM(actionValues.purchase)/SUM(COST)`, usar só `purchase` (não `omni_/web_in_store_/offsite_`). Cabeçalho obrigatório na saída: `projectDocumentId | platform | período | tool | provider=nekt`.
