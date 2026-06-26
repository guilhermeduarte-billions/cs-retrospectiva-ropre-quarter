# Pilares da retrospectiva — o que cada um analisa e de onde vem

Cada pilar segue: **DADOS** (com proveniência) → **APRENDIZADOS** (certo/errado + causa-raiz) → **SLOT DE AÇÃO**.

## 1. Tráfego — *NEKT (Meta + Google, se conectado)*
- **Avalie cada campanha pela métrica do SEU `goal`** (tabela E.1 em `fontes-mcp.md`). Só compare campanhas **dentro do mesmo objetivo**. Campanha de engajamento/Visitas ao Perfil com 0 leads **não é fracasso** → avalie por custo/engajamento, reações, saves, video views, custo/seguidor (`like`).
- Melhores/piores **campanhas** por objetivo: LEADS→CPL · Conversão→ROAS · TRAFFIC→CPC/Connect Rate · ENGAJAMENTO→custo/engajamento. Ranking **campanha → conjunto → anúncio**.
- **Públicos/segmentações**: ler de `groupName`/`campaignName` por heurística. Sem regex fixo — nomenclatura varia por coordenação.
- **Ambientes**: Connect Rate = `landing_page_view`/`link_click`; Conversion Rate = conversão/`landing_page_view`.
- **Conversão por modelo**: Inside Sales → leads/CPL/MQL/SQL (cockpit); E-commerce → compras/receita/**ROAS**/CPA (catálogo/remarketing vs frio).
- Custo por venda / lead **qualificado**: cruzar funil cockpit / CRM; slot se ausente.

## 2. Criativo / Comunicação / Copy — *NEKT creative_summary + ad-level*
- **Criativo vencedor** (mais leads/compras, melhor CPL/ROAS) e **criativo com mais conversões**.
- Métricas: CTR (link), CPL/CPA, **Hook Rate** (`video_view`/impr), formato (vídeo vs estático).
- **Copy/CTA**: `creative_summary.body` + `title` (analisar ângulo/promessa).
- Fadiga (padrão `creative-analyst`): CTR ↓ ~20% + frequência alta → sinalizar refresh.
- Preview/imagem do criativo = **slot** (não vem no creative_summary).

## 3. Gestão de Projetos — *Ekyte (entregas reais) + cockpit `deliveries_*`*
- **Detalhar TUDO que foi entregue ao cliente no quarter** via Ekyte (ver `fontes-mcp.md` §G):
  - Preferir `textSearch` pelo nome do cliente + datas de conclusão do quarter.
  - Validar que os títulos são do cliente certo (workspaceId sozinho pode misturar).
  - **Listar cada tarefa** (data + título), excluindo rotinas (ATWPP, weekly, sprint).
- Volume por tipo, SLA Ekyte, demandas atrasadas, anomalias/plano de ação (cockpit `deliveries_*`).

## 4. Cliente — *FONTE PRIMÁRIA: BigQuery Calls + WhatsApp (transcrições reais). Cockpit = apoio.*

⚠️ **Separar rigorosamente quem fala.** Na transcrição, identifique o **speaker** (cliente vs V4/Colli). Nunca misture fala do time V4 na seção do cliente.

### Blocos da seção 7

| Bloco | Quem fala | Conteúdo |
|-------|-----------|----------|
| **7a. Síntese de sentimento (IA)** | Neutro (agente) | Evolução do tom no quarter — sem atribuir citações. Lê calls + WhatsApp. **Não** copiar `call_transcription_summary_reasoning` do cockpit. |
| **7b. O que o CLIENTE disse** | **Só o cliente** | Verbatim literal: elogios + pontos de atenção. Formato: `"frase"` — **[Cliente · Call AAAA-MM-DD]** ou **[Cliente · WhatsApp DD/MM]**. Se não der para isolar o speaker → slot. |
| **7c. Conquistas do quarter (time V4)** | **Só V4/Colli** | O que o time comunicou como vitória/entrega na call **ou** conquistas objetivas dos dados (métrica, entrega, marco). Formato: `"frase"` — **[V4 — Papel/Nome · Call]** **ou** bullet factual `[NEKT]`/`[Ekyte]`/`[Cockpit]`. |
| **7d. Apoio quantitativo** | Cockpit | Scores por vertical, CSAT/NPS, WhatsApp status. |

**Regra:** `call_transcription_summary_reasoning` do cockpit é **pista interna** — pode alimentar 7a, mas **não** vai para 7b nem 7c sem validar speaker na transcrição.

Sem BigQuery → slots explícitos em 7b e 7c; 7c ainda pode listar conquistas **objetivas** dos dados (NEKT, Ekyte, cockpit).

## 5. CRM / Funil — *cockpit `paid_traffic_*`/`results_*` + CRM audit*
- Funil do **quarter**: Leads → MQL → SQL → Vendas → Receita. Colunas sempre **Projetado (meta) | Realizado | Pacing** — leitura esquerda→direita.
- Identificar o **gargalo** do trimestre e, se houver dados mensais no cockpit, a **evolução** (ex. pacing de leads caiu de abr→jun).
- **Critério MQL** do cliente: `paid_traffic_mql_sql_criteria`.
- Detalhe (tempo de etapa, ticket, **compra vs recompra**) → `dados-kommo-audit`/`dados-activecampaign-audit`; recompra = slot se não houver.
- Resultado vs meta: `results_goal_*` (sinalizar divergências entre campos).

## Mapeamento achado → integrante (para a matriz seção 8)
| Achado | Integrante |
|---|---|
| Campanha ineficiente, verba mal alocada, CPL/ROAS ruim | Paid media specialist (ou coord, se não houver) |
| Criativo fraco, fadiga, pedido de "criativos melhores" | Designer |
| Copy/ângulo, promessa fraca | Copywriter |
| Funil trava (SQL→venda), qualificação, recompra | AM / CRM analyst |
| Backlog atrasado, SLA, demandas | PM / Coordenador |
| Resultado/meta, divergência de dados | Coordenador (DRI) |
