#!/usr/bin/env python3
"""
Tarsila News — HTML Renderer
Reads JSON state from stdin, writes final designed email HTML to stdout.
Mirror of the editor's generateEmailHTML() function.

Usage: cat state.json | python3 render.py > email.html
"""
import json
import re
import sys
from datetime import datetime
from html import escape

LOGO_URL = "https://tarsila-editor.pages.dev/tarsila-logo.png"
ACCENT = "#2340DE"
INK = "#0A0A0A"
MUTED = "#6B6B6B"
LINE = "#E8E8E8"
BG = "#FAFAF7"
PAPER = "#FFFFFF"
BG_OUTER = "#F7F3EE"


def esc(s):
    if s is None:
        return ""
    return escape(str(s), quote=True)


def extract_youtube_id(url):
    if not url:
        return ""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


def fmt_date(iso):
    if not iso:
        return ""
    try:
        dt = datetime.strptime(iso, "%Y-%m-%d")
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                  "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        return f"{dt.day:02d} {months[dt.month-1]} {dt.year}"
    except Exception:
        return iso


def render_kicker(k):
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:14px;"><tr>
    <td style="width:24px; height:2px; background:{ACCENT}; font-size:0; line-height:0;">&nbsp;</td>
    <td style="padding-left:12px; font-family:'Inter',Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:{ACCENT};">{esc(k or "")}</td>
</tr></table>'''


def render_block(b):
    t = b.get("type")
    kicker = render_kicker(b.get("kicker"))

    if t in ("big", "product"):
        paras = "\n".join(
            f'<p style="font-family:\'Inter\',Arial,sans-serif; font-size:15px; line-height:1.55; color:#2A2A2A; margin:14px 0 12px;">{esc(p)}</p>'
            for p in (b.get("body") or "").split("\n\n")
        )
        title_html = (
            f'<a href="{esc(b.get("link"))}" style="color:{INK}; text-decoration:none;">{esc(b.get("title"))}</a>'
            if b.get("link") else esc(b.get("title"))
        )
        why_html = (
            f'<p style="font-family:\'Inter\',Arial,sans-serif; font-size:13px; line-height:1.55; color:{MUTED}; font-style:italic; margin:12px 0 0;">Por que importa: {esc(b.get("why"))}</p>'
            if b.get("why") else ""
        )
        return f'''<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}
<div style="font-family:'Fraunces',Georgia,serif; font-size:24px; font-weight:500; line-height:1.2; letter-spacing:-0.01em; color:{INK}; margin-bottom:14px;">{title_html}</div>
{paras}
{why_html}
</td></tr>'''

    if t == "quick":
        items = b.get("items") or []
        parts = []
        for i, it in enumerate(items):
            is_last = i == len(items) - 1
            border = "" if is_last else f"border-bottom:1px dashed {LINE};"
            pb = "0" if is_last else "20px"
            pt = "0" if i == 0 else "20px"
            title_html = (
                f'<a href="{esc(it.get("url"))}" style="color:{INK}; text-decoration:none; border-bottom:1px solid {LINE};">{esc(it.get("title"))}</a>'
                if it.get("url") else esc(it.get("title"))
            )
            tag_html = (
                f'<div style="display:inline-block; font-family:\'Inter\',Arial,sans-serif; font-size:9px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:{ACCENT}; background:#EDF0FE; padding:2px 6px; border-radius:2px; margin-bottom:6px;">{esc(it.get("tag"))}</div><br>'
                if it.get("tag") else ""
            )
            parts.append(f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="{border}"><tr>
<td valign="top" width="40" style="padding:{pt} 0 {pb}; font-family:'Fraunces',Georgia,serif; font-size:22px; color:{ACCENT}; font-weight:500; line-height:1;">{i+1:02d}</td>
<td valign="top" style="padding:{pt} 0 {pb} 8px;">
{tag_html}
<div style="font-family:'Inter',Arial,sans-serif; font-size:15px; font-weight:600; color:{INK}; margin-bottom:4px;">{title_html}</div>
<div style="font-family:'Inter',Arial,sans-serif; font-size:13px; color:{MUTED}; line-height:1.5;">{esc(it.get("desc"))}</div>
</td></tr></table>''')
        return f'<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}{"".join(parts)}</td></tr>'

    if t == "showcase":
        items = (b.get("items") or [])[:3]
        n = len(items)
        w = 504 if n == 1 else (246 if n == 2 else 160)
        cards = []
        for it in items:
            img = (
                f'<a href="{esc(it.get("link","#"))}" target="_blank" style="text-decoration:none;"><img src="{esc(it.get("image"))}" width="{w}" alt="" style="display:block; width:100%; height:auto;"></a>'
                if it.get("image") else f'<div style="background:#F0EDE8; height:{int(w*0.75)}px;"></div>'
            )
            link_html = (
                f'<a href="{esc(it.get("link"))}" target="_blank" style="font-family:\'Inter\',Arial,sans-serif; font-size:11px; color:{ACCENT}; font-weight:600; text-decoration:none; letter-spacing:0.06em; text-transform:uppercase;">Ver projeto →</a>'
                if it.get("link") else ""
            )
            cards.append(f'''<td valign="top" width="{w}" style="padding:0 6px; background:{BG};">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
<tr><td style="padding:0; line-height:0; font-size:0;">{img}</td></tr>
<tr><td style="padding:12px 14px 14px;">
<div style="font-family:'Inter',Arial,sans-serif; font-size:14px; font-weight:600; line-height:1.3; color:{INK}; margin-bottom:4px;">{esc(it.get("title") or "")}</div>
<div style="font-family:'Inter',Arial,sans-serif; font-size:11px; color:{MUTED}; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:6px;">{esc(it.get("creator") or "")}</div>
{link_html}
</td></tr></table></td>''')
        return f'''<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:0 -6px;"><tr>{"".join(cards)}</tr></table>
</td></tr>'''

    if t == "tool":
        why_html = (
            f'<p style="font-family:\'Inter\',Arial,sans-serif; font-size:12px; line-height:1.5; color:{MUTED}; font-style:italic; margin:0;">Por que importa: {esc(b.get("why"))}</p>'
            if b.get("why") else ""
        )
        return f'''<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
<td style="background:{BG}; border-left:3px solid {ACCENT}; padding:24px 28px;">
<div style="font-family:'Fraunces',Georgia,serif; font-size:20px; font-weight:500; color:{INK}; margin-bottom:8px;">{esc(b.get("name"))}</div>
<p style="font-family:'Inter',Arial,sans-serif; font-size:14px; line-height:1.55; color:#2A2A2A; margin:0 0 10px;">{esc(b.get("body"))}</p>
{why_html}
</td></tr></table>
</td></tr>'''

    if t == "meme":
        return f'''<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}
<p style="font-family:'Fraunces',Georgia,serif; font-size:18px; line-height:1.45; color:{INK}; font-style:italic; margin:0 0 8px;">"{esc(b.get("quote"))}"</p>
<p style="font-family:'Inter',Arial,sans-serif; font-size:13px; color:{MUTED}; margin:0;">{esc(b.get("attr"))}</p>
</td></tr>'''

    if t == "placeholder":
        return f'''<tr><td style="padding:40px 48px; border-bottom:1px solid {LINE};">{kicker}
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
<td style="background:#EDF0FE; border:1px dashed {ACCENT}; padding:20px 24px;">
<div style="font-family:'Inter',Arial,sans-serif; font-size:13px; color:{MUTED}; font-style:italic;">{esc(b.get("body"))}</div>
</td></tr></table>
</td></tr>'''

    if t == "trilha":
        vid = extract_youtube_id(b.get("videoUrl", ""))
        thumb = f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg" if vid else ""
        watch_url = f"https://www.youtube.com/watch?v={vid}" if vid else "#"
        play_svg = (
            "data:image/svg+xml;utf8,"
            "%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%2772%27%20height%3D%2772%27%20viewBox%3D%270%200%2072%2072%27%3E%3Ccircle%20cx%3D%2736%27%20cy%3D%2736%27%20r%3D%2736%27%20fill%3D%27%232340DE%27/%3E%3Cpolygon%20points%3D%2728%2C22%2028%2C50%2052%2C36%27%20fill%3D%27%23FFFFFF%27/%3E%3C/svg%3E"
        )
        thumb_html = (
            f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:20px;"><tr><td style="position:relative; padding:0; line-height:0; font-size:0;">
<a href="{watch_url}" target="_blank" style="text-decoration:none; display:block; position:relative;">
<img src="{thumb}" width="504" alt="" style="display:block; width:100%; max-width:504px; height:auto; border:0;">
<div style="position:absolute; top:0; left:0; right:0; bottom:0; display:flex; align-items:center; justify-content:center;"><img src="{play_svg}" width="72" height="72" alt="" style="display:block;"></div>
</a></td></tr></table>'''
            if vid else ""
        )
        return f'''<tr><td style="background:{INK}; padding:40px 48px;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;"><tr>
<td style="width:24px; height:2px; background:#FFFFFF; font-size:0; line-height:0;">&nbsp;</td>
<td style="padding-left:12px; font-family:'Inter',Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:#FFFFFF;">🎧 Trilha da edição</td>
</tr></table>
{thumb_html}
<div style="font-family:'Fraunces',Georgia,serif; font-size:22px; font-weight:500; color:#FFFFFF; margin-bottom:6px; line-height:1.2;">{esc(b.get("title") or "[Nome da música — Artista]")}</div>
<div style="font-family:'Inter',Arial,sans-serif; font-size:11px; letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.6); margin-bottom:20px;">Indicação de {esc(b.get("by") or "[membro do time]")}</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="background:{ACCENT}; padding:12px 22px;"><a href="{watch_url}" target="_blank" style="font-family:'Inter',Arial,sans-serif; font-size:13px; font-weight:600; color:#FFFFFF; text-decoration:none; letter-spacing:0.04em;">▶ &nbsp;Ouvir no YouTube</a></td>
</tr></table>
</td></tr>'''

    return ""


def render_html(state):
    blocks_html = "".join(render_block(b) for b in (state.get("blocks") or []))
    edition = esc(state.get("edition") or "")
    date_str = esc(fmt_date(state.get("date") or ""))
    lead = esc(state.get("lead") or "")
    preheader = esc(state.get("preheader") or "")

    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt-BR"><head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tarsila News — Edição {edition}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&display=swap" rel="stylesheet">
</head><body style="margin:0; padding:0; background:{BG_OUTER}; font-family:'Inter', Arial, sans-serif;">
<div style="display:none; max-height:0; overflow:hidden; font-size:1px; line-height:1px; color:{BG_OUTER}; opacity:0;">{preheader}</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:{BG_OUTER};"><tr><td align="center" style="padding:32px 16px;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="background:{PAPER}; max-width:600px;">
<tr><td align="center" style="padding:48px 48px 28px;">
<img src="{LOGO_URL}" width="320" alt="Tarsila" style="display:block; width:320px; max-width:80%; height:auto; margin:0 auto 12px;">
<div style="font-family:'Inter',Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.22em; text-transform:uppercase; color:{INK}; margin-top:4px;">News <span style="color:{ACCENT}; font-weight:800; letter-spacing:0;">·</span> Quinzenal <span style="color:{ACCENT}; font-weight:800; letter-spacing:0;">·</span> Design + Produto</div>
<div style="font-family:'Fraunces',Georgia,serif; font-size:15px; font-style:italic; font-weight:400; color:{MUTED}; letter-spacing:-0.005em; margin-top:10px;">Curadoria do time DWS × dentsu</div>
</td></tr>
<tr><td style="padding:0 48px 8px;"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-top:1px solid {LINE};"><tr>
<td style="padding-top:16px; font-family:'Inter',Arial,sans-serif; font-size:11px; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:{INK};">Edição {edition}</td>
<td align="right" style="padding-top:16px; font-family:'Inter',Arial,sans-serif; font-size:11px; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:{MUTED};">{date_str} · Quinzenal</td>
</tr></table></td></tr>
<tr><td style="padding:32px 48px 8px; font-family:'Fraunces',Georgia,serif; font-size:26px; line-height:1.28; font-weight:400; color:{INK}; letter-spacing:-0.015em;">{lead}</td></tr>
{blocks_html}
<tr><td style="padding:32px 48px 48px; background:{PAPER};"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
<td style="font-family:'Inter',Arial,sans-serif; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color:{MUTED};">Tarsila News · Nº {edition}</td>
<td align="right" style="font-family:'Fraunces',Georgia,serif; font-size:12px; font-style:italic; color:{MUTED};">by DWS × dentsu</td>
</tr><tr><td colspan="2" style="padding-top:16px; font-family:'Inter',Arial,sans-serif; font-size:10px; color:#B0B0B0; line-height:1.5;">Você recebeu porque faz parte do time DWS. Sugestões: responda esse email.</td></tr>
</table></td></tr>
</table></td></tr></table></body></html>'''


if __name__ == "__main__":
    state = json.load(sys.stdin)
    sys.stdout.write(render_html(state))
