#!/usr/bin/env node
/** Fetch Ekyte tasks Q2/2026 → _data/{TICKER}-ekyte.json */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dir = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dir, '_data');
fs.mkdirSync(OUT, { recursive: true });

function loadEkyteToken() {
  if (process.env.EKYTE_MCP_TOKEN) return process.env.EKYTE_MCP_TOKEN;
  for (const cfg of [
    `${process.env.HOME}/.cursor/mcp.json`,
    `${process.env.HOME}/.claude/mcp.json`,
  ]) {
    if (!fs.existsSync(cfg)) continue;
    const j = JSON.parse(fs.readFileSync(cfg, 'utf8'));
    const url = j?.mcpServers?.ekyte?.url || j?.servers?.ekyte?.url;
    const m = url?.match(/token=([^&]+)/);
    if (m) return m[1];
  }
  throw new Error('EKYTE token não encontrado (EKYTE_MCP_TOKEN ou mcp.json)');
}

const TOKEN = loadEkyteToken();
const EKYTE_URL = `https://api.ekyte.com/mcp?token=${TOKEN}`;

async function ekyteCall(tool, args) {
  const res = await fetch(EKYTE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: tool, arguments: args } }),
  });
  const text = await res.text();
  let msg;
  if (text.includes('\ndata:')) {
    const lines = text.split('\n').filter((l) => l.startsWith('data:')).map((l) => l.slice(5).trim());
    msg = JSON.parse(lines[lines.length - 1] || '{}');
  } else {
    msg = JSON.parse(text || '{}');
  }
  if (msg.error) throw new Error(JSON.stringify(msg.error));
  const content = msg.result?.content || [];
  const textItem = content.find((c) => c.type === 'text');
  if (!textItem) return msg.result;
  try {
    return JSON.parse(textItem.text);
  } catch {
    return textItem.text;
  }
}

const QUERIES = [
  {
    ticker: 'TROPM',
    args: {
      limit: 200,
      situation: '30',
      concludedDateStart: '2026-04-01',
      concludedDateEnd: '2026-06-30',
      textSearch: 'Tropical',
      textKey: 300,
    },
  },
  {
    ticker: 'UMBRO',
    args: {
      limit: 200,
      situation: '30',
      concludedDateStart: '2026-04-01',
      concludedDateEnd: '2026-06-30',
      workspaceId: '138963',
    },
  },
];

for (const q of QUERIES) {
  console.error(`== ${q.ticker} ekyte ==`);
  const raw = await ekyteCall('list_tasks', q.args);
  const tasks = Array.isArray(raw) ? raw : raw?.data || raw?.items || [];
  fs.writeFileSync(path.join(OUT, `${q.ticker}-ekyte.json`), JSON.stringify(tasks, null, 2));
  console.error(`  ${tasks.length} tasks`);
}

console.error('Done.', OUT);
