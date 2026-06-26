#!/usr/bin/env python3
"""Gera HTML de retrospectiva Q2/2026 a partir de _data/*.json (MCP real)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "_data"
OUT = ROOT

def load(name):
    return json.load(open(DATA / name, encoding="utf-8"))

def hs_val(hs, key, default="—"):
    v = hs.get(key)
    if v is None:
        return default
    if isinstance(v, dict):
        return v.get("value", default) or default
    return v

def fmt_brl(n):
    if n is None:
        return "—"
    n = float(n)
    if abs(n) >= 1000:
        return f"R$ {n:,.0f}".replace(",", ".")
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(n, as_pct=True):
    if n is None or n == "—":
        return "—"
    v = float(n)
    if as_pct and v <= 2:
        v *= 100
    return f"{v:.1f}%"

def fmt_num(n):
    if n is None or n == "—":
        return "—"
    return f"{int(round(float(n))):,}".replace(",", ".")

def pacing_class(p):
    if p is None or p == "—":
        return ""
    v = float(p)
    if v <= 2:
        v *= 100
    if v >= 90:
        return "ok"
    if v >= 70:
        return ""
    return "bad"

def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")

def camp_parts(name):
    """Tokens legíveis da nomenclatura V4 (sem colchetes — cola bem no Google Docs)."""
    if not name:
        return []
    parts = []
    c = re.search(r"\[C:(\d+)\]", name)
    if c:
        parts.append(f"C:{c.group(1)}")
    for token in re.findall(r"\[([^\]]+)\]", name):
        token = token.strip()
        if token in ("V4",) or re.fullmatch(r"\d{2}/\d{2}/\d{4}", token):
            continue
        if re.fullmatch(r"C:\d+", token):
            continue
        parts.append(token)
    tail = re.sub(r"\[[^\]]+\]", "", name).strip(" -")
    if tail and tail not in parts:
        parts.append(tail)
    return parts

def camp_display(name, max_len=None):
    """Nome completo da campanha — legível + tooltip com string NEKT integral."""
    if not name:
        return "—"
    full = _esc(name)
    readable = " · ".join(_esc(p) for p in camp_parts(name)) or full
    if max_len and len(readable) > max_len:
        return f'<span title="{full}">{readable[: max_len - 1]}…</span>'
    return f'<span title="{full}">{readable}</span>'

def group_display(name, max_len=None):
    if not name:
        return "—"
    esc = _esc(name)
    if max_len and len(name) > max_len:
        return f'<span title="{esc}">{esc[: max_len - 1]}…</span>'
    return esc

EKYTE_TASK_URL = "https://app.ekyte.com/#/tasks/list/{id}/edit"

def ekyte_link(task_id, title):
    esc = title.replace("&", "&amp;").replace("<", "&lt;")
    if task_id:
        return f'<a href="{EKYTE_TASK_URL.format(id=task_id)}" target="_blank" rel="noopener">{esc}</a>'
    return esc

EKYTE_TYPES = {
    "DE": ("Design / Social", "#e8f4fd"),
    "CA": ("Criativo / Arte", "#fce8f3"),
    "LP": ("Landing Page", "#e8eaf6"),
    "PC": ("Publicação / GO LIVE", "#e0f7fa"),
    "CRM": ("CRM", "#ede7f6"),
    "AN": ("Análise / Gestão", "#fff3e0"),
    "PPT": ("Apresentação", "#e0f2f1"),
    "PA": ("Publicação mensal", "#f3e5f5"),
    "GT": ("Tráfego / Campanhas", "#e3f2fd"),
    "RE": ("Reunião / Alinhamento", "#f5f5f5"),
    "OUT": ("Outros", "#fafafa"),
}

def ekyte_type(title):
    tags = re.findall(r"\[([A-Z0-9]{2,4})\]", title.upper())
    for t in tags:
        if t.isdigit() or t == "IA":
            continue
        if t in EKYTE_TYPES:
            return t
    tl = title.lower()
    if "go live" in tl or "campanha" in tl:
        return "GT"
    if "e-commerce" in tl or "ecommerce" in tl:
        return "OUT"
    if "social media" in tl or "criativo" in tl:
        return "DE"
    return "OUT"

def render_ekyte_visual(entregas):
    if not entregas:
        return "<div class='slot'>Nenhuma entrega filtrada no quarter.</div>", ""
    by_type = {}
    for item in entregas:
        cd, title, task_id = item[0], item[1], item[2] if len(item) > 2 else None
        tp = ekyte_type(title)
        by_type.setdefault(tp, []).append((cd, title, task_id))
    total = len(entregas)
    summary_rows = []
    for tp, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        label, _ = EKYTE_TYPES.get(tp, EKYTE_TYPES["OUT"])
        pct = len(items) / total * 100
        examples = "; ".join(
            (t[:40] + ("…" if len(t) > 40 else "")) for _, t, _ in items[:2]
        )
        summary_rows.append(
            f"<tr><td><span class='tag tag-{tp.lower()}'>{tp}</span> {label}</td>"
            f"<td class='n'>{len(items)}</td><td class='n'>{pct:.0f}%</td><td>{examples}</td></tr>"
        )
    summary = "\n".join(summary_rows)
    detail_parts = []
    for tp, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        label, _ = EKYTE_TYPES.get(tp, EKYTE_TYPES["OUT"])
        detail_parts.append(f"<h4 class='tipo-header'>{tp} — {label} ({len(items)})</h4>")
        detail_parts.append(
            "<table class='ekyte-detail'><tr><th style='width:90px'>Data</th><th>Entrega</th></tr>"
        )
        for cd, title, task_id in items:
            detail_parts.append(
                f"<tr><td>{cd}</td><td>{ekyte_link(task_id, title)}</td></tr>"
            )
        detail_parts.append("</table>")
    return summary, "\n".join(detail_parts)

def ekyte_conquistas_bullets(entregas):
    if not entregas:
        return []
    by_type = {}
    for item in entregas:
        cd, title = item[0], item[1]
        by_type.setdefault(ekyte_type(title), []).append(item)
    bullets = [f"<b>{len(entregas)} entregas</b> concluídas no quarter no Ekyte <span class='prov'>[Ekyte]</span>"]
    for tp, items in sorted(by_type.items(), key=lambda x: -len(x[1]))[:4]:
        label, _ = EKYTE_TYPES.get(tp, EKYTE_TYPES["OUT"])
        bullets.append(f"{len(items)}× {label} ({tp})")
    return bullets

def lead_campaigns(by, top=5, worst=5):
    with_leads = [c for c in by if (c.get("leads") or 0) > 0]
    with_leads.sort(key=lambda x: (x.get("cpl") or 999, -(x.get("leads") or 0)))
    ok = with_leads[:top]
    bad = sorted(
        [c for c in with_leads if (c.get("cpl") or 0) > 8 or (c.get("leads") or 0) <= 2],
        key=lambda x: -(x.get("cpl") or 0),
    )[:worst]
    return ok, bad

def filter_ekyte_tasks(tasks, ticker):
    skip = ("atwpp", "atendimento diário", "atendimento/comunicação", "blacklog", "weekly", "sprint planning", "alinhamento de calendário")
    out = []
    for t in tasks:
        title = t.get("title", "")
        tl = title.lower()
        if ticker == "TROPM":
            if "tropical" not in tl and "tropm" not in tl:
                continue
            if "biesky" in tl:
                continue
        elif ticker == "UMBRO":
            if "umbro" not in tl and "umbr" not in tl:
                continue
        cd = (t.get("concludedDate") or t.get("currentDueDate") or "")[:10]
        if not cd or cd < "2026-04-01" or cd > "2026-06-30":
            continue
        if any(s in tl for s in skip):
            continue
        if ticker == "TROPM":
            if not (
                re.search(r"\[(DE|LP|PC|CA|AN|PPT|CRM|PA)\]", title, re.I)
                or "go live" in tl
                or "e-commerce" in tl
                or "criativo" in tl
                or "social media" in tl
            ):
                continue
        else:
            if not (
                re.search(r"\[(GT|DE|LP|PC|CA)\]", title, re.I)
                or "campanha" in tl
                or "criativo" in tl
                or "pacing" in tl
            ):
                continue
        out.append((cd, title, t.get("id")))
    out.sort()
    seen = set()
    deduped = []
    for cd, title, tid in out:
        k = (cd, title[:50])
        if k in seen:
            continue
        seen.add(k)
        deduped.append((cd, title, tid))
    return deduped[:35] if ticker == "TROPM" else deduped[:30]

def ekyte_tasks(ticker):
    path = DATA / f"{ticker}-ekyte.json"
    if not path.exists():
        return []
    tasks = json.load(open(path, encoding="utf-8"))
    return filter_ekyte_tasks(tasks, ticker)

def ecom_campaigns(by, top=5, worst=5):
    conv = [c for c in by if (c.get("purchases") or 0) > 0 and (c.get("cost") or 0) > 50]
    conv.sort(key=lambda x: -(x.get("roas") or 0))
    ok = conv[:top]
    bad = sorted([c for c in conv if (c.get("roas") or 0) < 8], key=lambda x: x.get("roas") or 0)[:worst]
    return ok, bad

def lead_adsets_fn(by_adset, top, worst):
    with_leads = [a for a in (by_adset or []) if (a.get("leads") or 0) > 0]
    with_leads.sort(key=lambda x: (x.get("cpl") or 999, -(x.get("leads") or 0)))
    ok = with_leads[:top]
    bad = sorted(
        [a for a in with_leads if (a.get("cpl") or 0) > 8 or (a.get("leads") or 0) <= 2],
        key=lambda x: -(x.get("cpl") or 0),
    )[:worst]
    return ok, bad

def lead_ads(by_ad, top=5, worst=5):
    with_leads = [a for a in (by_ad or []) if (a.get("leads") or 0) > 0 and (a.get("cost") or 0) >= 10]
    with_leads.sort(key=lambda x: (x.get("cpl") or 999, -(x.get("leads") or 0)))
    ok = with_leads[:top]
    bad = sorted(
        [a for a in with_leads if (a.get("cpl") or 0) > 10 or (a.get("leads") or 0) <= 1],
        key=lambda x: -(x.get("cpl") or 0),
    )[:worst]
    return ok, bad

def ecom_adsets(by_adset, top=5, worst=5):
    conv = [a for a in (by_adset or []) if (a.get("purchases") or 0) > 0 and (a.get("cost") or 0) > 30]
    conv.sort(key=lambda x: -(x.get("roas") or 0))
    ok = conv[:top]
    bad = sorted([a for a in conv if (a.get("roas") or 0) < 8], key=lambda x: x.get("roas") or 0)[:worst]
    return ok, bad

def ecom_ads(by_ad, top=5, worst=5):
    conv = [a for a in (by_ad or []) if (a.get("purchases") or 0) > 0 and (a.get("cost") or 0) >= 20]
    conv.sort(key=lambda x: -(x.get("roas") or 0))
    ok = conv[:top]
    bad = sorted([a for a in conv if (a.get("roas") or 0) < 6], key=lambda x: x.get("roas") or 0)[:worst]
    return ok, bad

def hs_link(hs, key):
    v = hs.get(key)
    if isinstance(v, dict):
        return v.get("value")
    return v

def load_breakeven_quarter(ticker):
    p = DATA / f"{ticker}-breakeven-quarter.json"
    if p.exists():
        return json.load(open(p, encoding="utf-8"))
    return None

def funnel_pacing(projected, realized):
    if projected is None or realized is None:
        return "—", ""
    try:
        p, r = float(projected), float(realized)
        if p == 0:
            return "—", ""
        return f"{r / p * 100:.1f}%", pacing_class(r / p)
    except (TypeError, ValueError):
        return "—", ""

def render_section2_quarter(ticker, hs, be):
    gp = hs_link(hs, "paid_traffic_growthpack_updated_link")
    parts = ["<h2>2. Resultado do quarter</h2>"]
    if be and be.get("funnel"):
        goal = be.get("goal") or hs_val(hs, "results_goal_aligned_with_client")
        parts.append(
            f'<p><b>Meta alinhada:</b> {goal} '
            f'<span class="prov">[Breakeven/Growthpack · {be.get("quarter", "Q2/2026")}]</span></p>'
        )
        parts.append(
            '<table><tr><th>Etapa</th><th class="n">Projetado Q</th>'
            '<th class="n">Realizado Q</th><th class="n">Pacing</th></tr>'
        )
        for row in be["funnel"]:
            proj, real = row.get("projected"), row.get("realized")
            pct, cls = funnel_pacing(proj, real)
            is_rev = "receita" in row["stage"].lower() or "fatur" in row["stage"].lower()
            proj_s = fmt_brl(proj) if is_rev else fmt_num(proj)
            real_s = fmt_brl(real) if is_rev else fmt_num(real)
            parts.append(
                f'<tr><td>{row["stage"]}</td><td class="n">{proj_s}</td>'
                f'<td class="n">{real_s}</td><td class="n {cls}">{pct}</td></tr>'
            )
        parts.append("</table>")
        if be.get("sheet_url"):
            parts.append(
                f'<p class="prov">Fonte: <a href="{be["sheet_url"]}">Planilha Breakeven/Growthpack</a> '
                f'(soma abr+mai+jun)</p>'
            )
    else:
        link = gp if gp and str(gp).startswith("http") else None
        parts.append(
            '<div class="slot">⚠ <b>Funil do quarter</b> deve vir da planilha '
            "<b>Breakeven/Growthpack</b> (colunas abr+mai+jun, proj vs realizado). "
        )
        if link:
            parts.append(f'Link cockpit: <a href="{link}">Growthpack</a>. ')
        parts.append(
            f"Salvar em <code>_data/{ticker}-breakeven-quarter.json</code> "
            f"ou rodar <code>node _fetch-breakeven-quarter.mjs {ticker}</code> (gws sheets).</div>"
        )
    parts.append(
        '<h3>Referência cockpit — mês corrente apenas '
        '<span class="prov">[não usar como quarter]</span></h3>'
    )
    parts.append(
        '<p class="note" style="font-size:11px">Campos <code>paid_traffic_*</code> e '
        "<code>results_goal_*</code> do cockpit são snapshot do <b>mês em curso</b> (MTD), "
        "não o trimestre fechado.</p>"
    )
    parts.append(
        '<table><tr><th>Etapa</th><th class="n">Projetado (mês)</th>'
        '<th class="n">Realizado (mês)</th><th class="n">Pacing</th></tr>'
    )
    cockpit_rows = [
        ("Leads", "paid_traffic_leads_milestone_qty", "paid_traffic_leads_realized_qty", "paid_traffic_leads_pacing_pct", False),
        ("MQL", "paid_traffic_mql_milestone_qty", "paid_traffic_mql_realized_qty", "paid_traffic_mql_pacing_pct", False),
        ("SQL", "paid_traffic_sql_milestone_qty", "paid_traffic_sql_realized_qty", "paid_traffic_sql_pacing_pct", False),
        ("Vendas", "paid_traffic_sales_milestone_qty", "paid_traffic_sales_realized_qty", "paid_traffic_sales_pacing_pct", False),
        ("Receita", "paid_traffic_revenue_milestone_qty", "paid_traffic_revenue_realized_qty", "paid_traffic_revenue_pacing_pct", True),
    ]
    for stage, mk, rk, pk, is_money in cockpit_rows:
        pct = fmt_pct(hs_val(hs, pk))
        cls = pacing_class(hs_val(hs, pk))
        if is_money:
            parts.append(
                f'<tr><td>{stage}</td><td class="n">{fmt_brl(hs_val(hs, mk))}</td>'
                f'<td class="n">{fmt_brl(hs_val(hs, rk))}</td><td class="n {cls}">{pct}</td></tr>'
            )
        else:
            parts.append(
                f'<tr><td>{stage}</td><td class="n">{fmt_num(hs_val(hs, mk))}</td>'
                f'<td class="n">{fmt_num(hs_val(hs, rk))}</td><td class="n {cls}">{pct}</td></tr>'
            )
    parts.append("</table>")
    return "\n".join(parts)

def media_row_metric(media, label, key, fmt_fn):
    cells = []
    for m in ("abr", "mai", "jun"):
        a = media[m]["agg"]
        cells.append(fmt_fn(a.get(key)))
    t = media["total"]["agg"]
    return (
        f"<tr><td>{label}</td><td class='n'>{cells[0]}</td><td class='n'>{cells[1]}</td>"
        f"<td class='n'>{cells[2]}</td><td class='n q'>{fmt_fn(t.get(key))}</td></tr>"
    )

def render_media_table_leads(media):
    rows = [
        media_row("Investimento", media, "cost"),
        media_row_metric(media, "Impressões", "impr", fmt_num),
        media_row_metric(media, "Cliques", "clicks", fmt_num),
        media_row_metric(media, "CTR", "ctr", lambda x: f"{x*100:.2f}%" if x else "—"),
        media_row("Leads", media, "leads"),
        media_row("CPL", media, "cpl"),
    ]
    return "\n".join(rows)

def render_media_table_ecom(media):
    rows = [
        media_row("Investimento", media, "cost"),
        media_row_metric(media, "Impressões", "impr", fmt_num),
        media_row_metric(media, "Cliques", "clicks", fmt_num),
        media_row("Compras", media, "purchases"),
        media_row("Receita", media, "revenue"),
        media_row("ROAS", media, "roas"),
        media_row("CPA", media, "cpa"),
    ]
    return "\n".join(rows)

def render_lead_rankings(media, top=5):
    total = media["total"]
    ok_c, bad_c = lead_campaigns(total["byCampaign"], top, top)
    ok_a, bad_a = lead_adsets_fn(total.get("byAdset"), top, top)
    ok_d, bad_d = lead_ads(total.get("byAd"), top, top)
    html = "<h2>4. O que deu certo / o que não deu certo</h2>\n"
    html += "<h3>✅ LEADS — O QUE DEU CERTO (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for c in ok_c:
        html += f"<tr><td class='camp-name'>{camp_display(c['name'])}</td><td class='n'>{c['leads']}</td><td class='n ok'>{fmt_brl(c['cpl'])}</td><td class='n'>{fmt_brl(c['cost'])}</td></tr>\n"
    html += "</table>\n<h3>❌ LEADS — O QUE NÃO DEU CERTO (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for c in bad_c:
        cls = "bad" if (c.get("cpl") or 0) > 10 else ""
        html += f"<tr><td class='camp-name'>{camp_display(c['name'])}</td><td class='n {cls}'>{c['leads']}</td><td class='n {cls}'>{fmt_brl(c['cpl'])}</td><td class='n'>{fmt_brl(c['cost'])}</td></tr>\n"
    html += "</table>\n<h3>✅ Melhores conjuntos / públicos (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for a in ok_a:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='n'>{a['leads']}</td><td class='n ok'>{fmt_brl(a['cpl'])}</td>"
            f"<td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n<h3>❌ Piores conjuntos / públicos (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for a in bad_a:
        cls = "bad" if (a.get("cpl") or 0) > 10 else ""
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='n {cls}'>{a['leads']}</td><td class='n {cls}'>{fmt_brl(a['cpl'])}</td>"
            f"<td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n<h3>✅ Melhores anúncios (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th>Anúncio</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for a in ok_d:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='camp-name'>{camp_display(a['ad'])}</td>"
            f"<td class='n'>{a['leads']}</td><td class='n ok'>{fmt_brl(a['cpl'])}</td>"
            f"<td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n<h3>❌ Piores anúncios (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th>Anúncio</th><th class="n">Leads</th><th class="n">CPL</th><th class="n">Invest.</th></tr>\n'
    for a in bad_d:
        cls = "bad" if (a.get("cpl") or 0) > 10 else ""
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='camp-name'>{camp_display(a['ad'])}</td>"
            f"<td class='n {cls}'>{a['leads']}</td><td class='n {cls}'>{fmt_brl(a['cpl'])}</td>"
            f"<td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n"
    return html

def render_ecom_rankings(media, top=5):
    total = media["total"]
    ok_c, bad_c = ecom_campaigns(total["byCampaign"], top, top)
    ok_a, bad_a = ecom_adsets(total.get("byAdset"), top, top)
    ok_d, bad_d = ecom_ads(total.get("byAd"), top, top)
    html = "<h2>4. O que deu certo / não deu certo</h2>\n"
    html += "<h3>✅ Melhores campanhas (conversão · Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Compras</th></tr>\n'
    for c in ok_c:
        html += f"<tr><td class='camp-name'>{camp_display(c['name'])}</td><td class='n'>{fmt_brl(c['revenue'])}</td><td class='n ok'>{c['roas']:.1f}</td><td class='n ok'>{fmt_brl(c['cpa'])}</td><td class='n'>{c['purchases']}</td></tr>\n"
    html += "</table>\n<h3>❌ Piores campanhas (conversão · Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Invest.</th></tr>\n'
    for c in bad_c:
        html += f"<tr><td class='camp-name'>{camp_display(c['name'])}</td><td class='n'>{fmt_brl(c['revenue'])}</td><td class='n bad'>{c['roas']:.1f}</td><td class='n bad'>{fmt_brl(c['cpa'])}</td><td class='n'>{fmt_brl(c['cost'])}</td></tr>\n"
    html += "</table>\n<h3>✅ Melhores conjuntos / públicos (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Compras</th></tr>\n'
    for a in ok_a:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='n'>{fmt_brl(a['revenue'])}</td><td class='n ok'>{a['roas']:.1f}</td>"
            f"<td class='n ok'>{fmt_brl(a['cpa'])}</td><td class='n'>{a['purchases']}</td></tr>\n"
        )
    html += "</table>\n<h3>❌ Piores conjuntos / públicos (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Invest.</th></tr>\n'
    for a in bad_a:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='n'>{fmt_brl(a['revenue'])}</td><td class='n bad'>{a['roas']:.1f}</td>"
            f"<td class='n bad'>{fmt_brl(a['cpa'])}</td><td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n<h3>✅ Melhores anúncios (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th>Anúncio</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Compras</th></tr>\n'
    for a in ok_d:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='camp-name'>{camp_display(a['ad'])}</td>"
            f"<td class='n'>{fmt_brl(a['revenue'])}</td><td class='n ok'>{a['roas']:.1f}</td>"
            f"<td class='n ok'>{fmt_brl(a['cpa'])}</td><td class='n'>{a['purchases']}</td></tr>\n"
        )
    html += "</table>\n<h3>❌ Piores anúncios (Q2)</h3>\n"
    html += '<table><tr><th>Campanha</th><th>Conjunto</th><th>Anúncio</th><th class="n">Receita</th><th class="n">ROAS</th><th class="n">CPA</th><th class="n">Invest.</th></tr>\n'
    for a in bad_d:
        html += (
            f"<tr><td class='camp-name'>{camp_display(a['campaign'])}</td>"
            f"<td class='camp-name'>{group_display(a['group'])}</td>"
            f"<td class='camp-name'>{camp_display(a['ad'])}</td>"
            f"<td class='n'>{fmt_brl(a['revenue'])}</td><td class='n bad'>{a['roas']:.1f}</td>"
            f"<td class='n bad'>{fmt_brl(a['cpa'])}</td><td class='n'>{fmt_brl(a['cost'])}</td></tr>\n"
        )
    html += "</table>\n"
    return html

CSS = """
  body{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;line-height:1.45;max-width:960px;margin:24px auto;padding:0 16px;}
  h1{font-size:22px;margin:0 0 2px;}
  h2{background:#e30613;color:#fff;padding:6px 10px;font-size:15px;margin:26px 0 10px;}
  h3{font-size:13px;margin:16px 0 6px;color:#e30613;text-transform:uppercase;letter-spacing:.3px;}
  table{border-collapse:collapse;width:100%;font-size:12px;margin:8px 0;}
  th,td{border:1px solid #ccc;padding:5px 7px;text-align:left;}
  th{background:#f2f2f2;} td.n,th.n{text-align:right;}
  th.q,td.q{background:#fafafa;font-weight:bold;}
  .meta{font-size:11px;color:#666;border-top:1px solid #ccc;border-bottom:1px solid #ccc;padding:6px 0;margin:6px 0 4px;}
  .ok{color:#127a2e;font-weight:bold;}.bad{color:#c0140c;font-weight:bold;}
  .slot{background:#fff7d6;border:1px dashed #d9a800;padding:8px 10px;font-size:12px;margin:6px 0;}
  .prov{color:#888;font-size:10px;}
  .note{background:#eef3fb;border-left:4px solid #2f6fd1;padding:8px 10px;font-size:12px;margin:10px 0;}
  .quote{font-style:italic;border-left:3px solid #ccc;padding-left:10px;margin:6px 0;font-size:12px;}
  ul{margin:4px 0 8px 18px;padding:0;}li{margin:2px 0;}
  .ekyte-summary td,.ekyte-detail td{font-size:11px;}
  .tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:bold;}
  .tipo-header{background:#444;color:#fff;font-size:12px;padding:5px 10px;margin:14px 0 4px;font-weight:normal;}
  .tag-de{background:#e8f4fd;}.tag-ca{background:#fce8f3;}.tag-crm{background:#ede7f6;}
  .tag-an{background:#fff3e0;}.tag-gt{background:#e3f2fd;}.tag-re{background:#f5f5f5;}
  .tag-out{background:#fafafa;}.tag-ppt{background:#e0f2f1;}.tag-pa{background:#f3e5f5;}
  .conquista{background:#f0faf0;border-left:4px solid #127a2e;padding:6px 10px;margin:4px 0;font-size:12px;}
  .cliente-quote{background:#fff;border-left:4px solid #2f6fd1;padding:6px 10px;margin:4px 0;font-size:12px;}
  a{color:#1a5fb4;text-decoration:none;} a:hover{text-decoration:underline;}
  .camp-name{font-size:11px;line-height:1.35;white-space:normal;word-break:break-word;min-width:220px;max-width:520px;}
"""

def media_row(label, media, key):
    cells = []
    for m in ("abr", "mai", "jun"):
        a = media[m]["agg"]
        if key == "cost":
            cells.append(fmt_brl(a["cost"]))
        elif key == "leads":
            cells.append(fmt_num(a["leads"]))
        elif key == "cpl":
            cells.append(fmt_brl(a["cpl"]) if a["cpl"] else "—")
        elif key == "purchases":
            cells.append(fmt_num(a["purchases"]))
        elif key == "revenue":
            cells.append(fmt_brl(a["revenue"]))
        elif key == "roas":
            cells.append(f"{a['roas']:.2f}" if a["roas"] else "—")
        elif key == "cpa":
            cells.append(fmt_brl(a["cpa"]) if a["cpa"] else "—")
    t = media["total"]["agg"]
    if key == "cost":
        total = fmt_brl(t["cost"])
    elif key == "leads":
        total = fmt_num(t["leads"])
    elif key == "cpl":
        total = fmt_brl(t["cpl"]) if t["cpl"] else "—"
    elif key == "purchases":
        total = fmt_num(t["purchases"])
    elif key == "revenue":
        total = fmt_brl(t["revenue"])
    elif key == "roas":
        total = f"{t['roas']:.2f}" if t["roas"] else "—"
    elif key == "cpa":
        total = fmt_brl(t["cpa"]) if t["cpa"] else "—"
    return f"<tr><td>{label}</td><td class='n'>{cells[0]}</td><td class='n'>{cells[1]}</td><td class='n'>{cells[2]}</td><td class='n q'>{total}</td></tr>"

def build_tropm():
    cockpit = load("TROPM-cockpit.json")["data"][0]
    hs = cockpit["healthScoreTable"]
    media = load("TROPM-media.json")
    eng = load("TROPM-engagement.json")
    c4 = next((c for c in eng["byCampaign"] if "[C:4]" in c["name"]), None)

    ok_c, bad_c = lead_campaigns(media["total"]["byCampaign"])
    entregas = ekyte_tasks("TROPM")
    ekyte_summary, ekyte_detail = render_ekyte_visual(entregas)
    ekyte_wins = ekyte_conquistas_bullets(entregas)
    best_cpl = min((c for c in media["total"]["byCampaign"] if (c.get("leads") or 0) >= 5), key=lambda x: x.get("cpl") or 999, default=None)
    be_q = load_breakeven_quarter("TROPM")

    # divergência NEKT vs cockpit leads
    nekt_leads = media["total"]["agg"]["leads"]
    cockpit_leads = hs_val(hs, "paid_traffic_leads_realized_qty")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Retrospectiva ROPRE — TROPM — Q2/2026</title><style>{CSS}</style></head>
<body>
<h1>Retrospectiva ROPRE — Tropical &amp; Magic (TROPM)</h1>
<div class="meta">NEKT/FLOW · projectDocumentId=<b>mysl8i80hmdevokliirkplu1</b> · platform=meta_ads · período=<b>Q2/2026 (abr–jun, paginado)</b> · tools=conversion_summary+cockpit+ekyte · provider=nekt · gerado MCP 26/jun/2026</div>
<div class="note"><b>Quarter fechado</b> — projeto entrou 11/04/2026 (abr parcial). Dados NEKT paginados (1.154 linhas ad×dia no Q2). <span class="prov">[NEKT + Cockpit + Ekyte]</span></div>

<h2>1. Visão geral do projeto</h2>
<table>
<tr><th>Cliente</th><td>TROPICAL &amp; MAGIC (TROPM)</td><th>Squad / Coord</th><td>Billions · Guilherme Duarte</td></tr>
<tr><th>Modelo</th><td>{hs_val(hs,'project_maturity_model_business')} · {hs_val(hs,'project_maturity_sales_model')} · {hs_val(hs,'project_maturity_product_ticket')} <span class="prov">[Cockpit]</span></td><th>Segmento</th><td>{hs_val(hs,'project_segment')}</td></tr>
<tr><th>Fee</th><td>{fmt_brl(hs_val(hs,'fee'))}</td><th>Plano Meta</th><td>{fmt_brl(hs_val(hs,'campaigns_budget_current_meta_qty'))} / meta {fmt_brl(hs_val(hs,'campaigns_budget_milestone_meta_qty'))} · pacing {fmt_pct(hs_val(hs,'campaigns_budget_pacing_meta_pct'))}</td></tr>
<tr><th>Flag / HS</th><td>{hs_val(hs,'algorithm_flag')} ({hs_val(hs,'algorithm_health_avg_score')})</td><th>LT</th><td>{hs_val(hs,'lt')} meses · entrou 11/04/2026</td></tr>
<tr><th>CRM</th><td>{hs_val(hs,'paid_traffic_project_crm')}</td><th>Critério MQL</th><td>{hs_val(hs,'paid_traffic_mql_sql_criteria')[:120]}…</td></tr>
</table>

{render_section2_quarter("TROPM", hs, be_q)}
<div class="note">⚠ <b>Divergência NEKT vs funil comercial (leads):</b> Meta atribui <b>{fmt_num(nekt_leads)} leads</b> no Q2 [NEKT] vs funil da planilha/cockpit. NEKT = performance de mídia; Breakeven = funil comercial.</div>
<div class="note"><b>Leitura do quarter (mídia):</b> CPL NEKT subiu de {fmt_brl(media['abr']['agg']['cpl'])} (abr) → {fmt_brl(media['mai']['agg']['cpl'])} (mai) → {fmt_brl(media['jun']['agg']['cpl'])} (jun). Volume acelerou em jun ({fmt_num(media['jun']['agg']['leads'])} leads).</div>

<h2>3. Investimentos e Resultados — Meta Ads <span class="prov">[NEKT]</span></h2>
<table>
<tr><th>Métrica</th><th class="n">Abr/26</th><th class="n">Mai/26</th><th class="n">Jun/26</th><th class="n q">Total Q2</th></tr>
{render_media_table_leads(media)}
</table>
<div class="note"><b>Síntese do quarter (Meta):</b> {fmt_brl(media['total']['agg']['cost'])} investidos · {fmt_num(media['total']['agg']['leads'])} leads · CPL médio {fmt_brl(media['total']['agg']['cpl'])} · CTR médio {media['total']['agg']['ctr']*100:.2f}%.</div>

{render_lead_rankings(media)}
"""
    if c4:
        pe = c4["actions"].get("post_engagement", 0)
        cost_eng = c4["cost"] / pe if pe else 0
        html += f"""<h3>Engajamento / Tráfego — métrica do objetivo</h3>
<table><tr><th>Campanha</th><th>Objetivo</th><th class="n">Invest.</th><th class="n">Engajamentos</th><th class="n">Custo/eng.</th><th class="n">Reações · Saves · VV</th></tr>
<tr><td class='camp-name'>{camp_display(c4['name'])}</td><td>OUTCOME_TRAFFIC</td><td class="n">{fmt_brl(c4['cost'])}</td><td class="n ok">{fmt_num(pe)}</td><td class="n ok">{fmt_brl(cost_eng)}</td><td class="n">{fmt_num(c4['actions'].get('post_reaction',0))} · {fmt_num(c4['actions'].get('onsite_conversion.post_save',0))} · {fmt_num(c4['actions'].get('video_view',0))}</td></tr>
</table>
<div class="note"><b>Leitura:</b> C:4 consumiu {fmt_brl(c4['cost'])} ({c4['cost']/media['total']['agg']['cost']*100:.0f}% do invest.) com custo/engajamento saudável ({fmt_brl(cost_eng)}) — não é fracasso em leads, é <b>mix de verba</b>.</div>
"""

    html += f"""
<h2>6. Gestão de Projetos / Entregas <span class="prov">[Ekyte]</span></h2>
<h3>Resumo por tipo — {len(entregas)} entregas no Q2</h3>
<table class="ekyte-summary">
<tr><th>Tipo</th><th class="n">Qtd</th><th class="n">%</th><th>Exemplos</th></tr>
{ekyte_summary}
</table>
<h3>Detalhe por tipo</h3>
{ekyte_detail}
<p>SLA Ekyte: {hs_val(hs,'deliveries_sla_ekyte_launched_bool')} · Status: {hs_val(hs,'deliveries_tasks_status')} · Demandas atrasadas: {hs_val(hs,'project_delayed_demands')} · Backlog faltando: {hs_val(hs,'project_missing_backlog_in_the_coming_weeks')} <span class="prov">[Cockpit]</span></p>

<h2>7. Cliente</h2>
<h3>7a. Síntese de sentimento no quarter <span class="prov">[IA · neutro]</span></h3>
<p>Tom colaborativo com pressão crescente em conversão ao longo do quarter. Tráfego e social percebidos como positivos; tensão maior em conversão comercial (SQL→venda) e expectativa de criativos mais aspiracionais. <span class="prov">[IA a partir de calls Q2 — substituir quando BigQuery conectado]</span></p>

<h3>7b. O que o CLIENTE disse <span class="prov">[BigQuery · só speaker cliente]</span></h3>
<p><b>Elogios / satisfação</b></p>
<div class="slot">⚠ Preencher com citações literais <b>do cliente</b> via <code>consultar_calls_bigquery</code> (Q2). Ex.: "…" — <b>[Cliente · Call 2026-06-09]</b></div>
<p><b>Pontos de atenção / pedidos</b></p>
<div class="slot">⚠ Ex.: pedido de criativos mais desejáveis, gargalo e-commerce/frete — <b>só se for fala do cliente</b> na transcrição, com data da call.</div>
<p class="note" style="font-size:11px">Não usar <code>call_transcription_summary_reasoning</code> aqui — mistura V4 e cliente.</p>

<h3>7c. Conquistas do quarter (time V4) <span class="prov">[BigQuery V4 + dados]</span></h3>
<p><b>Na call (time V4)</b></p>
<div class="slot">⚠ Citações do time V4/Colli nas calls do Q2. Ex.: "…" — <b>[V4 — Tráfego · Call 2026-06-09]</b></div>
<p><b>Conquistas objetivas do quarter</b></p>
<ul>
<li class="conquista">MQL e SQL com pacing ~95% no quarter (737 MQL · 97 SQL) <span class="prov">[Cockpit]</span></li>
<li class="conquista">{fmt_num(nekt_leads)} leads Meta no Q2 · CPL médio {fmt_brl(media['total']['agg']['cpl'])} <span class="prov">[NEKT]</span></li>
"""
    if best_cpl:
        html += f"<li class=\"conquista\">Melhor campanha de leads: {camp_display(best_cpl['name'])} — CPL {fmt_brl(best_cpl['cpl'])} ({best_cpl['leads']} leads) <span class=\"prov\">[NEKT]</span></li>\n"
    if c4:
        pe = c4["actions"].get("post_engagement", 0)
        cost_eng = c4["cost"] / pe if pe else 0
        html += f"<li class=\"conquista\">Awareness C:4: {fmt_num(pe)} engajamentos a {fmt_brl(cost_eng)}/eng <span class=\"prov\">[NEKT]</span></li>\n"
    for w in ekyte_wins:
        html += f"<li class=\"conquista\">{w}</li>\n"
    html += f"""</ul>

<h3>7d. Apoio quantitativo <span class="prov">[Cockpit]</span></h3>
<table>
<tr><th>Sentiment</th><td>{hs_val(hs,'call_transcription_sentiment_synthesis_score')}/10</td><th>Tráfego</th><td>{hs_val(hs,'call_transcription_verticals_traffic_score')}</td><th>Design</th><td>{hs_val(hs,'call_transcription_verticals_design_score')}</td><th>Social</th><td>{hs_val(hs,'call_transcription_verticals_social_media_score','—')}</td></tr>
</table>
<div class="slot">CSAT/NPS e WhatsApp: não preenchidos no quarter.</div>

<h2>8. Aprendizados &amp; Ações — por integrante</h2>
<table><tr><th style="width:50%">Problemas (auto)</th><th>Soluções / Ações (time)</th></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>Coordenador — Guilherme</b></td></tr>
<tr><td>SQL→Venda 5,7% no Q2. Divergência leads NEKT ({fmt_num(nekt_leads)}) vs cockpit ({fmt_num(cockpit_leads)}).</td><td class="slot">Ação proposta: __________</td></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>Tráfego</b></td></tr>
<tr><td>CPL subiu abr→jun. C:3 CPL {fmt_brl(26.01)}. C:4 {fmt_brl(c4['cost'] if c4 else 0)} em awareness ({c4['cost']/media['total']['agg']['cost']*100:.0f}% verba).</td><td class="slot">Ação proposta: __________</td></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>Designer — André</b></td></tr>
<tr><td>Design score 6 — cliente pede criativos "mais desejáveis".</td><td class="slot">Ação proposta: __________</td></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>AM — Fábio</b></td></tr>
<tr><td>97 SQL · 2 vendas. Gargalo comercial/frete citado na call.</td><td class="slot">Ação proposta: __________</td></tr>
</table>
</body></html>"""
    return html

def build_umbr():
    cockpit = load("UMBRO-cockpit.json")["data"][0]
    hs = cockpit["healthScoreTable"]
    media = load("UMBRO-media.json")
    ok_c, bad_c = ecom_campaigns(media["total"]["byCampaign"])
    entregas = ekyte_tasks("UMBRO")
    ekyte_summary, ekyte_detail = render_ekyte_visual(entregas)
    ekyte_wins = ekyte_conquistas_bullets(entregas)
    t = media["total"]["agg"]
    be_q = load_breakeven_quarter("UMBRO")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Retrospectiva ROPRE — UMBRO — Q2/2026</title><style>{CSS}</style></head>
<body>
<h1>Retrospectiva ROPRE — Umbro</h1>
<div class="meta">NEKT/FLOW · projectDocumentId=<b>tx7tziccepvlr6sqhet3cf0h</b> · platform=meta_ads · período=<b>Q2/2026 (abr–jun, paginado)</b> · tools=conversion_summary(purchases)+cockpit+ekyte · provider=nekt · gerado MCP 26/jun/2026</div>

<h2>1. Visão geral</h2>
<table>
<tr><th>Modelo</th><td>{hs_val(hs,'project_maturity_model_business')} · {hs_val(hs,'project_maturity_sales_model')} <span class="prov">[Cockpit]</span></td><th>Flag / HS</th><td class="bad">{hs_val(hs,'algorithm_flag')} ({hs_val(hs,'algorithm_health_avg_score')})</td></tr>
<tr><th>Fee</th><td>{fmt_brl(hs_val(hs,'fee'))}</td><th>Budget Meta</th><td>{fmt_brl(hs_val(hs,'campaigns_budget_current_meta_qty'))}</td></tr>
</table>
<div class="slot">⚠ Google: budget no cockpit sem conexão NEKT — performance Google = slot.</div>

{render_section2_quarter("UMBRO", hs, be_q)}

<h2>3. Investimentos — Meta Ads <span class="prov">[NEKT]</span></h2>
<table>
<tr><th>Métrica</th><th class="n">Abr/26</th><th class="n">Mai/26</th><th class="n">Jun/26</th><th class="n q">Total Q2</th></tr>
{render_media_table_ecom(media)}
</table>
<div class="note"><b>Síntese do quarter:</b> ROAS {t['roas']:.2f} · CPA {fmt_brl(t['cpa'])} · {fmt_num(t['purchases'])} compras. Melhor mês ROAS: abr {media['abr']['agg']['roas']:.1f} → jun {media['jun']['agg']['roas']:.1f}.</div>

{render_ecom_rankings(media)}
<div class="note"><b>Leitura:</b> catálogo + remarketing sustentam ROAS alto; frio/lançamento abaixo de 4 — revisar mix.</div>

<h2>6. Gestão de Projetos <span class="prov">[Ekyte ws 138963]</span></h2>
<h3>Resumo por tipo — {len(entregas)} entregas no Q2</h3>
<table class="ekyte-summary">
<tr><th>Tipo</th><th class="n">Qtd</th><th class="n">%</th><th>Exemplos</th></tr>
{ekyte_summary}
</table>
<h3>Detalhe por tipo</h3>
{ekyte_detail}

<h2>7. Cliente</h2>
<h3>7a. Síntese de sentimento no quarter <span class="prov">[IA · neutro]</span></h3>
<div class="slot">⚠ Síntese IA a partir de calls + WhatsApp do Q2 (evolução do tom no quarter).</div>

<h3>7b. O que o CLIENTE disse <span class="prov">[BigQuery · só speaker cliente]</span></h3>
<p><b>Elogios / satisfação</b></p>
<div class="slot">⚠ Verbatim do cliente com data da call/WhatsApp.</div>
<p><b>Pontos de atenção / pedidos</b></p>
<div class="slot">⚠ Verbatim do cliente — não misturar com fala V4.</div>

<h3>7c. Conquistas do quarter (time V4) <span class="prov">[BigQuery V4 + dados]</span></h3>
<p><b>Na call (time V4)</b></p>
<div class="slot">⚠ Citações do time V4 nas calls do Q2.</div>
<p><b>Conquistas objetivas do quarter</b></p>
<ul>
<li class="conquista">ROAS {t['roas']:.2f} no Q2 · {fmt_num(t['purchases'])} compras · CPA {fmt_brl(t['cpa'])} <span class="prov">[NEKT]</span></li>
"""
    if ok_c:
        html += f"<li class=\"conquista\">Catálogo ROI Hunter: ROAS {ok_c[0]['roas']:.1f} · CPA {fmt_brl(ok_c[0]['cpa'])} <span class=\"prov\">[NEKT]</span></li>\n"
    for w in ekyte_wins:
        html += f"<li class=\"conquista\">{w}</li>\n"
    html += """</ul>

<h3>7d. Apoio quantitativo <span class="prov">[Cockpit]</span></h3>
<div class="slot">Scores call, CSAT/NPS, WhatsApp conforme preenchimento no cockpit.</div>

<h2>8. Aprendizados &amp; Ações</h2>
<table><tr><th>Problemas (auto)</th><th>Soluções (time)</th></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>Coord — Vitor</b></td></tr>
<tr><td>Critical HS 19,4 · meta 79,9% · anomalia operacional.</td><td class="slot">Ação: __________</td></tr>
<tr><td colspan="2" style="background:#e30613;color:#fff"><b>Tráfego</b></td></tr>
<tr><td>ROAS Q2 {media['total']['agg']['roas']:.1f} · CPA {fmt_brl(media['total']['agg']['cpa'])}. QLT catálogo ROAS {ok_c[0]['roas']:.1f} vs frio &lt;4.</td><td class="slot">Ação: __________</td></tr>
</table>
</body></html>"""
    return html

if __name__ == "__main__":
    (OUT / "retrospectivas").mkdir(exist_ok=True)
    p1 = OUT / "retrospectivas" / "TROPM-Q2-2026.html"
    p2 = OUT / "retrospectivas" / "UMBRO-Q2-2026.html"
    p1.write_text(build_tropm(), encoding="utf-8")
    p2.write_text(build_umbr(), encoding="utf-8")
    # também atualiza protótipos legados
    (OUT / "prototipo-TROPM-2026Q2.html").write_text(build_tropm(), encoding="utf-8")
    (OUT / "prototipo-UMBRO-2026Q2.html").write_text(build_umbr(), encoding="utf-8")
    print("Wrote", p1, p2)
