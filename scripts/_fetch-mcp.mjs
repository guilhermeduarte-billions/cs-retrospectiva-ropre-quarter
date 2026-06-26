#!/usr/bin/env node
/**
 * One-shot MCP caller for Flow/Cockpit (reads ~/.config/colli/mcp.env)
 * Usage: node _fetch-mcp.mjs <toolName> '<json args>'
 */
import https from 'https';
import fs from 'fs';
import { URL } from 'url';

const MCP_URL = 'https://mcp-cockpit.dados.collieassociados.com/mcp';
const ENV_PATH = `${process.env.HOME}/.config/colli/mcp.env`;

function loadEnv() {
  const out = {};
  if (!fs.existsSync(ENV_PATH)) return out;
  for (const line of fs.readFileSync(ENV_PATH, 'utf8').split('\n')) {
    if (!line || line.startsWith('#')) continue;
    const i = line.indexOf('=');
    if (i === -1) continue;
    let v = line.slice(i + 1).trim();
    if (v.length >= 2 && (v[0] === '"' || v[0] === "'") && v[0] === v.at(-1)) v = v.slice(1, -1);
    out[line.slice(0, i).trim()] = v;
  }
  return out;
}

const env = { ...loadEnv(), ...process.env };
const JWT = env.MCP_COCKPIT_JWT;
const GATEWAY = env.MCP_GATEWAY_TOKEN;
if (!JWT || !GATEWAY) {
  console.error(`Missing MCP_COCKPIT_JWT / MCP_GATEWAY_TOKEN in ${ENV_PATH}`);
  process.exit(1);
}

let sessionId = null;
let reqId = 1;

function post(body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const url = new URL(MCP_URL);
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json, text/event-stream',
      Authorization: `Bearer ${JWT}`,
      'x-mcp-gateway': GATEWAY,
      'Content-Length': Buffer.byteLength(data),
    };
    if (sessionId) headers['mcp-session-id'] = sessionId;

    const req = https.request(
      { hostname: url.hostname, path: url.pathname, method: 'POST', headers },
      (res) => {
        if (res.headers['mcp-session-id']) sessionId = res.headers['mcp-session-id'];
        const ct = res.headers['content-type'] || '';
        let buf = '';
        res.on('data', (c) => { buf += c; });
        res.on('end', () => {
          const out = [];
          if (ct.includes('text/event-stream')) {
            for (const line of buf.split('\n')) {
              if (line.startsWith('data: ')) {
                const s = line.slice(6).trim();
                if (s) try { out.push(JSON.parse(s)); } catch {}
              }
            }
          } else {
            try { out.push(JSON.parse(buf)); } catch {}
          }
          if (res.statusCode >= 400) reject(new Error(`HTTP ${res.statusCode}: ${buf.slice(0, 500)}`));
          else resolve(out);
        });
      }
    );
    req.on('error', reject);
    req.setTimeout(120000, () => req.destroy(new Error('timeout')));
    req.write(data);
    req.end();
  });
}

async function rpc(method, params, { notification = false } = {}) {
  const id = notification ? undefined : reqId++;
  const body = { jsonrpc: '2.0', method, params };
  if (!notification) body.id = id;
  const msgs = await post(body);
  if (notification) return null;
  const r = msgs.find((m) => m.id === id) || msgs[msgs.length - 1];
  if (r?.error) throw new Error(JSON.stringify(r.error));
  return r?.result;
}

async function callTool(name, args) {
  const result = await rpc('tools/call', { name, arguments: args });
  if (result?.content) {
    const text = result.content.filter((c) => c.type === 'text').map((c) => c.text).join('\n');
    try { return JSON.parse(text); } catch { return text; }
  }
  return result;
}

const toolName = process.argv[2];
const argsJson = process.argv[3] || '{}';

await rpc('initialize', {
  protocolVersion: '2024-11-05',
  capabilities: {},
  clientInfo: { name: 'retro-fetch', version: '1.0' },
});
await rpc('notifications/initialized', {}, { notification: true });

const args = JSON.parse(argsJson);
const data = await callTool(toolName, args);
console.log(JSON.stringify(data, null, 2));
