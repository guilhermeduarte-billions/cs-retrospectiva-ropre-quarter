# cs-retrospectiva-ropre-quarter

Skill de agente (Claude Code, Cursor, Codex) para **gerar retrospectiva de Growth Marketing do quarter** — insumo de reuniões **ROPRE**: mídia (NEKT), cockpit/FLOW, Ekyte, funil Breakeven/Growthpack e (opcional) BigQuery → HTML renderizado + **publicação automática no Google Docs** + registro na planilha de Strategy Review.

**Autor:** [@guilhermeduarte-billions](https://github.com/guilhermeduarte-billions)  
**Versão da skill:** 1.3.0

---

## ⚠️ Aviso — work in progress

Esta skill está **em iteração ativa**. APIs, parsers e o piloto de scripts podem mudar sem aviso prévio.

- Validada em operação real (Q2/2026), mas **não é produto oficial** da V4 Company.
- Requer MCPs e credenciais que **você** configura (cockpit/FLOW, Ekyte, etc.) — nada disso vem no repo.
- Outputs são **rascunhos para reunião**: o time preenche soluções/ações; o agente não inventa dado ausente (usa *slots*).
- Issues e PRs são bem-vindos; breaking changes são esperados até uma versão **1.x estável**.

Use por sua conta em ambiente de franquia/cliente. Não commitar credenciais, IDs de cliente ou planilhas privadas.

---

## O que faz

Fluxo **macro → micro → publicação**:

1. Descobre projetos do coordenador (**cockpit/FLOW** + planilha-mestra de GrowthPacks do squad)
2. **Macro:** Realizado consolidado do quarter pelo **GrowthPack** (Projetado × Realizado + split por canal) — não existe no FLOW (cockpit é MTD)
3. **Micro:** estratifica via **NEKT** (campanha → conjunto/público → anúncio → keyword) e **reconcilia NEKT × GrowthPack**
4. Lista entregas **Ekyte** com links
5. Gera HTML com 8 seções + matriz Problemas | Soluções (ações em branco)
6. **Publica no Google Docs** via `python-docx` + Drive API (`drive.files().update()`) — tabelas nativas, cores V4, slots amarelos; link permanente preservado
7. **Registra o link** na planilha de Strategy Review via Sheets API (coluna "Retrospectiva AI" + checkbox "Retrospectiva (By AI)")

**Mídia = só NEKT.** O que o NEKT não entrega vira *slot* sinalizado para iteração — a skill **nunca** puxa de API de plataforma.

Diferente de `analise-ropre-quarter` (avalia um ROPRE pronto). Esta skill **produz** o conteúdo a partir de dados MCP.

---

## Novidades (v1.3.x)

- **Passo 7 — Publicação automática no Google Docs.** Após salvar o HTML, a skill gera um `.docx` via `python-docx` e faz upload via `drive.files().update()` — o Google Doc tem o conteúdo substituído sem mudar o link (mesmo `fileId`). Por que `.docx` e não HTML direto: upload de HTML quebra tabelas e CSS; a conversão `.docx → Google Docs` é fiel (tabelas com bordas, headers vermelhos V4 `#E30613`, slots amarelos `#FFF7D6`).
- **Registro na planilha de Strategy Review.** Link gravado via Sheets API (coluna U = link, coluna O = `TRUE`). Config do spreadsheet é parâmetro — agnóstico ao squad/Brain.
- **Validado** em 8 projetos no piloto Q2/2026 (ASSO, LATI, SICA, CDGF, FIEE, SINQ, EZBU, TROPM).

## Novidades (v1.2.x)

- **GrowthPack = Realizado consolidado do quarter (macro→micro).** O Realizado do quarter não está no FLOW; vem da aba *Acompanhamento Mensal* do GrowthPack. Descoberta via planilha-mestra do squad (fallback: campo do cockpit). Acesso por Google Drive MCP / export CSV público / service account.
- **Mídia = só NEKT.** Proibido contornar por API de plataforma; lacuna do NEKT vira slot para iteração.
- **Cadeia de ranking não-pulável:** campanha → conjunto/público → anúncio → keyword. Keywords só via NEKT; quando o conector não sincroniza o stream, é *slot de ausência confirmada*.
- **Vencedores detalhados** (Status + critério de leitura) e **reconciliação NEKT × GrowthPack** obrigatória por canal.

---

## Instalação

### Opção A — Claude Code / Cursor (cópia manual)

```bash
git clone https://github.com/guilhermeduarte-billions/cs-retrospectiva-ropre-quarter.git
cp -R cs-retrospectiva-ropre-quarter/.claude/skills/cs-retrospectiva-ropre-quarter \
  ~/.claude/skills/
```

No Cursor, o agente também lê `~/.claude/skills/` e espelhos em `.claude/skills/` do projeto.

### Opção B — Só ler a skill no repo

Abra `.claude/skills/cs-retrospectiva-ropre-quarter/SKILL.md` e referências em `references/`.

---

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| MCP **cockpit** / FLOW | `cockpit_query_table`, `flow_media_*`, conexões NEKT |
| MCP **ekyte** | Entregas concluídas no quarter |
| MCP **BigQuery** (opcional) | Verbatim cliente vs V4 nas calls |
| Planilha **Growthpack/Breakeven** | Funil projetado × realizado do quarter |
| **python-docx** + **google-api-python-client** | Passo 7 — geração do .docx e upload para o Google Drive |
| Credenciais Google (`drive` scope) | `credentials/google_drive_token.json` — para Drive + Sheets API |

Configure MCP no seu agente (`~/.cursor/mcp.json`, `~/.claude/mcp.json`, etc.). A skill assume **zero base local** — tudo via MCP em runtime.

---

## Scripts opcionais (piloto)

Pasta `scripts/` — pipeline testado que grava JSON em `_data/` e renderiza HTML:

```bash
cd scripts
node _run-fetch.mjs          # cockpit + NEKT (demora — paginação)
node _fetch-ekyte.mjs
node _fetch-breakeven-quarter.mjs TICKER
python3 _build-html.py
```

Requer `MCP_COCKPIT_JWT` / `MCP_GATEWAY_TOKEN` (ex.: `~/.config/.../mcp.env`). **Não** inclua esse arquivo no git.

---

## Uso no agente

```
/cs-retrospectiva-ropre-quarter
```

Ou: *"faz a retrospectiva do quarter do cliente X para o ROPRE"*.

O agente deve ler `SKILL.md` e `references/fontes-mcp.md` antes de chamar tools.

---

## Estrutura

```
.claude/skills/cs-retrospectiva-ropre-quarter/
  SKILL.md                 # instruções principais
  references/              # fontes MCP, pilares, template, runtime
  assets/                  # template HTML base
  CHANGELOG.md
scripts/                   # piloto opcional (fetch + build HTML)
```

---

## Licença

MIT — veja [LICENSE](LICENSE).
