#!/usr/bin/env node
/** Batch fetch for retrospectiva Q2/2026 — TROPM + UMBRO */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __dir = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dir, '_data');
fs.mkdirSync(OUT, { recursive: true });

const PROJECTS = [
  { ticker: 'TROPM', documentId: 'mysl8i80hmdevokliirkplu1', ekyteWs: '134937', preset: 'leads', model: 'inside' },
  { ticker: 'UMBRO', documentId: 'tx7tziccepvlr6sqhet3cf0h', ekyteWs: null, preset: 'purchases', model: 'ecom' },
];

const MONTHS = [
  { key: 'abr', start: '2026-04-01T00:00:00Z', end: '2026-05-01T00:00:00Z' },
  { key: 'mai', start: '2026-05-01T00:00:00Z', end: '2026-06-01T00:00:00Z' },
  { key: 'jun', start: '2026-06-01T00:00:00Z', end: '2026-07-01T00:00:00Z' },
];
const Q2 = { start: '2026-04-01T00:00:00Z', end: '2026-07-01T00:00:00Z' };

function mcp(tool, args) {
  const r = spawnSync('node', [path.join(__dir, '_fetch-mcp.mjs'), tool, JSON.stringify(args)], {
    encoding: 'utf8',
    maxBuffer: 50 * 1024 * 1024,
  });
  if (r.status !== 0) throw new Error(`${tool}: ${r.stderr || r.stdout}`);
  return JSON.parse(r.stdout);
}

function save(name, data) {
  fs.writeFileSync(path.join(OUT, name), JSON.stringify(data, null, 2));
}

async function paginateConversion(pid, period, preset, extra = {}) {
  const rows = [];
  let offset = 0;
  const limit = 500;
  for (;;) {
    const res = mcp('flow_media_conversion_summary', {
      projectDocumentId: pid,
      platform: 'meta_ads',
      period: { startGte: period.start, endLt: period.end },
      actionPresets: extra.actionPresets || [preset],
      actionTypes: extra.actionTypes,
      pagination: { limit, offset },
    });
    const batch = res?.data?.items || res?.rows || res?.data?.rows || [];
    if (!batch.length) break;
    rows.push(...batch);
    if (batch.length < limit) break;
    offset += limit;
    if (offset > 20000) break; // safety
  }
  return rows;
}

function aggRows(rows) {
  let cost = 0, impr = 0, clicks = 0, leads = 0, purchases = 0, revenue = 0;
  const actions = {};
  for (const row of rows) {
    const m = row.metrics || {};
    cost += Number(m.COST || 0);
    impr += Number(m.IMPRESSIONS || 0);
    clicks += Number(m.CLICKS || 0);
    const a = row.actions || {};
    for (const [k, v] of Object.entries(a)) {
      actions[k] = (actions[k] || 0) + Number(v || 0);
    }
    const av = row.actionValues || {};
    revenue += Number(av.purchase || 0);
  }
  leads = Number(actions.lead || 0);
  purchases = Number(actions.purchase || 0);
  return {
    cost, impr, clicks, leads, purchases, revenue, actions,
    cpl: leads ? cost / leads : null,
    cpa: purchases ? cost / purchases : null,
    roas: cost ? revenue / cost : null,
    ctr: impr ? clicks / impr : null,
  };
}

function aggByCampaign(rows) {
  const map = {};
  for (const row of rows) {
    const name = row.dimensions?.campaignName || row.dimensions?.campaignId || '?';
    if (!map[name]) map[name] = [];
    map[name].push(row);
  }
  const out = [];
  for (const [name, rs] of Object.entries(map)) {
    const a = aggRows(rs);
    out.push({ name, ...a });
  }
  return out.sort((x, y) => (y.leads || y.purchases || 0) - (x.leads || x.purchases || 0));
}

function aggByAdset(rows) {
  const map = {};
  for (const row of rows) {
    const campaign = row.dimensions?.campaignName || row.dimensions?.campaignId || '?';
    const group = row.dimensions?.groupName || row.dimensions?.groupId || '?';
    const key = `${campaign}\0${group}`;
    if (!map[key]) map[key] = { campaign, group, rows: [] };
    map[key].rows.push(row);
  }
  const out = [];
  for (const { campaign, group, rows: rs } of Object.values(map)) {
    const a = aggRows(rs);
    out.push({ campaign, group, ...a });
  }
  return out.sort((x, y) => (y.leads || y.purchases || 0) - (x.leads || x.purchases || 0));
}

function aggByAd(rows) {
  const map = {};
  for (const row of rows) {
    const campaign = row.dimensions?.campaignName || row.dimensions?.campaignId || '?';
    const group = row.dimensions?.groupName || row.dimensions?.groupId || '?';
    const ad = row.dimensions?.adName || row.dimensions?.adId || '?';
    const key = `${campaign}\0${group}\0${ad}`;
    if (!map[key]) map[key] = { campaign, group, ad, rows: [] };
    map[key].rows.push(row);
  }
  const out = [];
  for (const { campaign, group, ad, rows: rs } of Object.values(map)) {
    const a = aggRows(rs);
    out.push({ campaign, group, ad, ...a });
  }
  return out.sort((x, y) => (y.leads || y.purchases || 0) - (x.leads || x.purchases || 0));
}

for (const p of PROJECTS) {
  console.error(`== ${p.ticker} cockpit ==`);
  const cockpit = mcp('cockpit_query_table', {
    search: p.ticker === 'TROPM' ? 'Tropical' : 'Umbro',
    pageSize: 1,
    resolveCalculations: true,
  });
  save(`${p.ticker}-cockpit.json`, cockpit);

  console.error(`== ${p.ticker} connections ==`);
  try {
    save(`${p.ticker}-connections.json`, mcp('flow_project_data_list_connections', { projectDocumentId: p.documentId }));
  } catch (e) {
    save(`${p.ticker}-connections.json`, { error: String(e) });
  }

  console.error(`== ${p.ticker} campaigns ==`);
  try {
    save(`${p.ticker}-campaigns.json`, mcp('flow_media_campaign_summary', {
      projectDocumentId: p.documentId,
      platform: 'meta_ads',
      period: { startGte: Q2.start, endLt: Q2.end },
      pagination: { limit: 100, offset: 0 },
    }));
  } catch (e) {
    save(`${p.ticker}-campaigns.json`, { error: String(e) });
  }

  const monthly = {};
  for (const mo of MONTHS) {
    console.error(`== ${p.ticker} ${mo.key} ==`);
    const rows = await paginateConversion(p.documentId, mo, p.preset);
    monthly[mo.key] = { rows: rows.length, agg: aggRows(rows), byCampaign: aggByCampaign(rows), byAdset: aggByAdset(rows), byAd: aggByAd(rows) };
  }
  console.error(`== ${p.ticker} Q2 total ==`);
  const q2rows = await paginateConversion(p.documentId, Q2, p.preset);
  monthly.total = { rows: q2rows.length, agg: aggRows(q2rows), byCampaign: aggByCampaign(q2rows), byAdset: aggByAdset(q2rows), byAd: aggByAd(q2rows) };
  save(`${p.ticker}-media.json`, monthly);

  if (p.ticker === 'TROPM') {
    console.error(`== TROPM engagement ==`);
    const engTypes = ['post_engagement', 'post_reaction', 'onsite_conversion.post_save', 'like', 'video_view', 'landing_page_view', 'link_click'];
    const engRows = await paginateConversion(p.documentId, Q2, p.preset, { actionPresets: ['all'], actionTypes: engTypes });
    save(`TROPM-engagement.json`, { agg: aggRows(engRows), byCampaign: aggByCampaign(engRows) });
  }
}

console.error('Done. Output in', OUT);
