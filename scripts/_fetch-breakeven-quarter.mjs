#!/usr/bin/env node
/**
 * Funil do QUARTER via planilha Growthpack/Breakeven.
 * Primário: export CSV público (sem gws). Fallback: gws sheets +read.
 * Saída: _data/{TICKER}-breakeven-quarter.json
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __dir = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dir, '_data');
const TICKER = process.argv[2] || 'TROPM';

function mcp(tool, args) {
  const r = spawnSync('node', [path.join(__dir, '_fetch-mcp.mjs'), tool, JSON.stringify(args)], {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
  });
  if (r.status !== 0) throw new Error(r.stderr || r.stdout);
  return JSON.parse(r.stdout);
}

function hsVal(hs, key) {
  const v = hs?.[key];
  return typeof v === 'object' && v ? v.value : v;
}

function sheetId(url) {
  const m = String(url || '').match(/\/d\/([a-zA-Z0-9-_]+)/);
  return m ? m[1] : null;
}

function gidFromUrl(url) {
  const m = String(url || '').match(/[?#&]gid=(\d+)/);
  return m ? m[1] : null;
}

function parseNum(s) {
  if (s == null || s === '' || s === '-') return null;
  let t = String(s).replace(/R\$\s?/g, '').replace(/%$/, '').trim();
  if (!t) return null;
  if (t.includes(',')) {
    t = t.replace(/\s/g, '').replace(/\./g, '').replace(',', '.');
  } else if ((t.match(/\./g) || []).length > 1 || /^\d{1,3}(\.\d{3})+$/.test(t)) {
    t = t.replace(/\./g, '');
  }
  const n = Number(t);
  return Number.isFinite(n) ? n : null;
}

/** Parser CSV mínimo (campos entre aspas). */
function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQ = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQ) {
      if (c === '"' && text[i + 1] === '"') {
        cell += '"';
        i++;
      } else if (c === '"') inQ = false;
      else cell += c;
    } else if (c === '"') inQ = true;
    else if (c === ',') {
      row.push(cell);
      cell = '';
    } else if (c === '\n' || (c === '\r' && text[i + 1] === '\n')) {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = '';
      if (c === '\r') i++;
    } else cell += c;
  }
  if (cell.length || row.length) {
    row.push(cell);
    rows.push(row);
  }
  return rows;
}

async function fetchCsv(spreadsheetId, gid) {
  const url = `https://docs.google.com/spreadsheets/d/${spreadsheetId}/export?format=csv&gid=${gid}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const text = await res.text();
  if (text.includes('<!DOCTYPE html>') || text.includes('Não foi possível')) return null;
  return text;
}

async function listGids(spreadsheetId) {
  const res = await fetch(`https://docs.google.com/spreadsheets/d/${spreadsheetId}/htmlview`);
  if (!res.ok) return [];
  const html = await res.text();
  const gids = [...html.matchAll(/gid=(\d+)/g)].map((m) => m[1]);
  return [...new Set(gids)];
}

function sumMonthCols(row, colStart = 1, n = 3) {
  let s = 0;
  let any = false;
  for (let i = colStart; i < colStart + n; i++) {
    const v = parseNum(row[i]);
    if (v != null) {
      s += v;
      any = true;
    }
  }
  return any ? s : null;
}

/** Realizado Q: aba Breakeven mensal (cols abr+mai+jun), bloco "Investimento Meta". */
function parseBreakevenRealized(rows) {
  let start = -1;
  for (let i = 0; i < rows.length; i++) {
    const a = (rows[i][0] || '').trim();
    if (/^Investimento Meta$/i.test(a)) {
      start = i + 1;
      break;
    }
  }
  if (start < 0) return null;

  const map = {
    Leads: 'Leads',
    'MQLs (manual)': 'MQL',
    'SQLs (manual)': 'SQL',
    'Vendas (manual)': 'Vendas',
    'Valor de venda (manual)': 'Receita',
  };
  const out = {};
  for (let i = start; i < rows.length; i++) {
    const label = (rows[i][0] || '').trim();
    if (!label) break;
    if (/^Investimento /i.test(label)) break;
    const stage = map[label];
    if (!stage) continue;
    out[stage] = sumMonthCols(rows[i], 1, 3);
  }
  return Object.keys(out).length ? out : null;
}

/** Projetado Q: aba com "Funil de vendas" (últimas colunas: qty + etapa). */
function parseProjectionFunnel(rows) {
  const flat = rows.map((r) => r.join(',')).join('\n');
  if (!/Funil de vendas/i.test(flat)) return null;

  const stageKey = {
    leads: 'Leads',
    mqls: 'MQL',
    sqls: 'SQL',
    vendas: 'Vendas',
  };
  const out = {};
  for (const row of rows) {
    if (row.length < 2) continue;
    const stageRaw = (row[row.length - 1] || '').trim().toLowerCase();
    const stage = stageKey[stageRaw];
    if (!stage) continue;
    const qty = parseNum(row[row.length - 2]);
    if (qty != null) out[stage] = qty;
  }
  return Object.keys(out).length ? out : null;
}

function buildFunnel(projected, realized, revenueProjected) {
  const stages = ['Leads', 'MQL', 'SQL', 'Vendas', 'Receita'];
  const funnel = [];
  for (const stage of stages) {
    const proj = stage === 'Receita' ? revenueProjected : projected?.[stage];
    const real = realized?.[stage];
    if (proj == null && real == null) continue;
    funnel.push({ stage, projected: proj, realized: real });
  }
  return funnel.length ? funnel : null;
}

function funnelFromCockpitRevenue(hs) {
  const projected = parseNum(hsVal(hs, 'results_goal_qty'));
  const realized = parseNum(hsVal(hs, 'results_goal_reached_qty'));
  if (projected == null && realized == null) return null;
  return [{ stage: 'Receita', projected, realized }];
}

const cockpit = mcp('cockpit_query_table', {
  search: TICKER === 'TROPM' ? 'Tropical' : 'Umbro',
  pageSize: 1,
  resolveCalculations: true,
});
const hs = cockpit?.data?.[0]?.healthScoreTable || {};
const sheetUrl = hsVal(hs, 'paid_traffic_growthpack_updated_link')
  || hsVal(hs, 'results_breakeven_spreadsheet_link');
const spreadsheetId = sheetId(sheetUrl);
const breakevenGid = gidFromUrl(sheetUrl);

const out = {
  ticker: TICKER,
  quarter: 'Q2/2026',
  months: ['abr', 'mai', 'jun'],
  goal: hsVal(hs, 'results_goal_aligned_with_client'),
  sheet_url: sheetUrl?.startsWith('http') ? sheetUrl : null,
  funnel: null,
  source: null,
  note: null,
};

if (!spreadsheetId) {
  out.fetch_error = 'Link da planilha não encontrado no cockpit';
  fs.writeFileSync(path.join(OUT, `${TICKER}-breakeven-quarter.json`), JSON.stringify(out, null, 2));
  console.error('Wrote (sem planilha)', path.join(OUT, `${TICKER}-breakeven-quarter.json`));
  process.exit(0);
}

let realized = null;
let projected = null;
let revenueProjected = parseNum(hsVal(hs, 'results_goal_qty'));

if (breakevenGid) {
  const csv = await fetchCsv(spreadsheetId, breakevenGid);
  if (csv) {
    realized = parseBreakevenRealized(parseCsv(csv));
    out.source = { breakeven_gid: breakevenGid, method: 'csv_export' };
  }
}

if (!realized || !projected) {
  const gids = await listGids(spreadsheetId);
  for (const gid of gids) {
    if (gid === breakevenGid) continue;
    const csv = await fetchCsv(spreadsheetId, gid);
    if (!csv) continue;
    const rows = parseCsv(csv);
    if (!projected) {
      const p = parseProjectionFunnel(rows);
      if (p) {
        projected = p;
        out.source = { ...(out.source || {}), projection_gid: gid };
      }
    }
  }
}

// E-commerce sem aba Breakeven mensal: receita do cockpit (meta alinhada)
const model = String(hsVal(hs, 'project_maturity_model_business') || '').toLowerCase();
const isEcom = model.includes('ecommerce') || model.includes('e-commerce');

if (isEcom && !realized) {
  const revReal = parseNum(hsVal(hs, 'paid_traffic_revenue_realized_qty'))
    ?? parseNum(hsVal(hs, 'results_goal_reached_qty'));
  const revProj = parseNum(hsVal(hs, 'paid_traffic_revenue_milestone_qty'))
    ?? revenueProjected;
  if (revReal != null || revProj != null) {
    realized = { Receita: revReal };
    revenueProjected = revProj ?? revenueProjected;
    out.note = 'E-commerce: funil da planilha ausente — receita via cockpit (growthpack não tem aba Breakeven mensal).';
  }
}

out.funnel = buildFunnel(projected, realized, revenueProjected);

if (!out.funnel) {
  const fb = funnelFromCockpitRevenue(hs);
  if (fb) {
    out.funnel = fb;
    out.note = 'Fallback: só meta de receita do cockpit (results_goal_*).';
  } else {
    out.fetch_error = 'Não foi possível parsear funil — verifique link/gid da planilha.';
  }
} else if (!out.note) {
  out.note = 'Projetado: aba Funil de vendas + results_goal_qty (Receita). Realizado: soma abr+mai+jun (Investimento Meta).';
}

if (realized?.Leads != null) {
  out.monthly_realized_meta = realized;
}
if (projected) {
  out.quarter_projected = projected;
}

fs.writeFileSync(path.join(OUT, `${TICKER}-breakeven-quarter.json`), JSON.stringify(out, null, 2));
console.error('Wrote', path.join(OUT, `${TICKER}-breakeven-quarter.json`), out.funnel ? `(${out.funnel.length} etapas)` : '(vazio)');
