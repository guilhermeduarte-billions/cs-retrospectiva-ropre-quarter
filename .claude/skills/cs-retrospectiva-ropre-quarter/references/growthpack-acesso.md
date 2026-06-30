# Acesso ao GrowthPack (Google Sheets) — 3 vias

O GrowthPack é a **fonte do Realizado consolidado do quarter** (não existe no FLOW). Ele é um Google Sheets. Esta skill é **agnóstica ao Brain** — não dependa de ingest local nem de paths pessoais. Qualquer pessoa do time precisa conseguir ler a planilha por **uma** das vias abaixo. Use a primeira que funcionar.

> ⚠️ **Não cacheie conteúdo de cliente.** O que é configurável e pode ser salvo é só: o `documentId` do próprio usuário e a **URL da planilha-mestra do squad**. Os GrowthPacks por projeto são lidos em runtime.

---

## Via 1 — Conector Google Drive (MCP) — preferida

Se o usuário tem o conector **Google Drive** ativo (tools `mcp__*_Google_Drive__*`), é a via mais limpa e respeita as permissões do próprio usuário.

1. **Achar o arquivo:** `search_files` com `query: "title contains 'GrowthPack' and title contains '<NOME DO CLIENTE>'"` (ou pelo `fileId` extraído do `Link do GrowthPack` da planilha-mestra — o ID é o trecho entre `/d/` e `/edit`).
2. **Ler conteúdo:** `read_file_content` com `fileId`. Retorna representação textual da planilha (todas as abas). Localize a aba **"Acompanhamento Mensal"**.
3. Se a representação textual embaralhar colunas (planilha larga), use `download_file_content` com `exportMimeType: "text/csv"` — mas atenção: o CSV exportado traz **só a primeira aba**. Para uma aba específica, prefira a Via 2 (precisa do `gid`).

**Quando falha:** usuário sem conector Drive, ou arquivo fora do Drive dele (não compartilhado). → Via 2 ou 3.

---

## Via 2 — Export CSV público (sem auth) — mais simples

Funciona se a planilha está compartilhada como **"qualquer pessoa com o link"** (a maioria dos GrowthPacks e a planilha-mestra do squad estão).

```
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}
```

- `SPREADSHEET_ID` e `GID` saem do `Link do GrowthPack` (`.../d/{ID}/edit?gid={GID}`).
- Baixe com `curl -sL "...&gid=..."`. **HTTP 200 + CSV** = ok. **HTTP 302/redireciono p/ accounts.google.com** = planilha não é pública → Via 1 ou 3.
- Para a aba "Acompanhamento Mensal" do template GrowthPack 3.0, o **gid padrão é `1422566774`** — mas confirme: alguns projetos têm gid diferente. Se o gid do link não for a aba de acompanhamento, teste `1422566774`; se ainda assim não bater, liste as abas via Via 1/3.

**Vantagem:** zero setup, funciona em qualquer máquina. **Limite:** só lê planilhas públicas.

---

## Via 3 — Service Account Google Cloud (programático, time todo)

Para automação que roda sem o login interativo de ninguém (CI, agente headless, planilha privada). **É isto que se ensina o time a criar.** Passo a passo:

### 3.1 Criar o projeto e a service account
1. Acesse **console.cloud.google.com** → crie/selecione um projeto (ex. `colli-growthpack`).
2. **APIs & Services → Enabled APIs → + Enable APIs** → habilite **Google Sheets API** e **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account**. Dê um nome (ex. `growthpack-reader`). Não precisa de role no projeto.
4. Na service account criada → aba **Keys → Add key → Create new key → JSON**. Baixa um `.json` com as credenciais. **Guarde com cuidado** (é segredo; nunca commitar).

### 3.2 Dar acesso às planilhas
A service account tem um e-mail tipo `growthpack-reader@colli-growthpack.iam.gserviceaccount.com`.
- **Opção A (recomendada):** compartilhe a **pasta do Drive** que contém os GrowthPacks com esse e-mail, como **Leitor**. Tudo dentro herda o acesso.
- **Opção B:** compartilhe cada planilha (mestra + GrowthPacks) individualmente com o e-mail, como Leitor.

### 3.3 Ler via API
Com o JSON da credencial, autentique e leia (qualquer linguagem). Esqueleto em Node:

```js
import { google } from "googleapis";
const auth = new google.auth.GoogleAuth({
  keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS, // caminho do JSON
  scopes: ["https://www.googleapis.com/auth/spreadsheets.readonly"],
});
const sheets = google.sheets({ version: "v4", auth });
const res = await sheets.spreadsheets.values.get({
  spreadsheetId: SPREADSHEET_ID,
  range: "Acompanhamento Mensal", // nome da aba, não o gid
});
const rows = res.data.values; // matriz linha×coluna
```

- Use o **nome da aba** no `range` (ex. `"Acompanhamento Mensal"`), não o gid.
- `GOOGLE_APPLICATION_CREDENTIALS` aponta para o JSON; não embuta a chave no código.
- Para listar abas de uma planilha: `sheets.spreadsheets.get({ spreadsheetId, fields: "sheets.properties(title,sheetId)" })` → casa `title` ↔ `gid`.

**Vantagem:** funciona com planilha privada, sem login humano, igual pra todo o time. **Setup:** ~10 min uma vez por squad.

---

## Resumo de decisão

| Situação | Via |
|----------|-----|
| Tenho conector Google Drive no Claude | **Via 1** |
| Planilha é pública ("qualquer um com link") | **Via 2** (curl CSV) |
| Planilha privada / automação headless / time todo | **Via 3** (service account) |

No piloto local do Guilherme, o ingest diário do Brain já traz as planilhas — mas isso é **conveniência pessoal, não requisito da skill**. A skill canônica usa Via 1/2/3.
