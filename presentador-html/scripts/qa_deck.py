#!/usr/bin/env python3
"""
qa_deck.py — Control de calidad OBLIGATORIO de una presentación generada.

Uso:
    python scripts/qa_deck.py <deck.html> [--out carpeta_qa] [--min-contrast 4.5]

Renderiza cada slide en Chromium (Playwright) a 1920×1080 y verifica:
  · texto desbordado o fuera del lienzo        · contraste de texto (WCAG)
  · requests externas (debe funcionar offline) · errores de consola / JS
  · fuentes cargadas                            · peso del archivo
Genera: <qa>/slide-XX.png, <qa>/contact-sheet.png (para revisión visual) y <qa>/report.json
Código de salida 0 = OK · 1 = hay errores que corregir.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECK_JS = r"""
(minContrast) => {
  const sl = document.querySelector('#stage > section.slide.active');
  const issues = [];
  const stage = document.querySelector('#stage').getBoundingClientRect();
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  function bgOf(el) {
    const layers = []; let e = el;
    while (e && e !== document.documentElement) {
      if (e.matches && e.matches('section.slide.has-bg')) return { image: true };  // texto sobre foto de fondo
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !cs.backgroundImage.startsWith('linear-gradient') && !cs.backgroundImage.startsWith('radial-gradient')) return { image: true };
      const c = parse(cs.backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
      e = e.parentElement;
    }
    // si la slide tiene foto de fondo, el texto está sobre imagen
    if (el.closest('section.slide.has-bg') && !layers.some(l => l.a >= 1)) return { image: true };
    let base = { r: 255, g: 255, b: 255, a: 1 };
    for (let k = layers.length - 1; k >= 0; k--) base = blend(layers[k], base);
    return { color: base };
  }
  const textEls = Array.from(sl.querySelectorAll('h1,h2,h3,p,li,span,strong,em,figcaption,cite,td,div.stat-value,div.stat-label,div.stat-note,div.tl-date,div.insight,div.sec-num,button'))
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden' && Array.from(e.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()); });
  for (const el of textEls) {
    const r = el.getBoundingClientRect();
    const txt = el.textContent.trim().slice(0, 60);
    if (r.right > stage.right + 2 || r.bottom > stage.bottom + 2 || r.left < stage.left - 2 || r.top < stage.top - 2)
      issues.push({ kind: 'fuera-del-lienzo', text: txt });
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight, 10) || 400;
    if (fs < 20 && !el.closest('.credit') && !el.closest('.source') && !el.closest('svg')) issues.push({ kind: 'texto-pequeno', text: txt, size: fs });
    const fg = parse(cs.color); const bg = bgOf(el);
    if (fg && bg.color && parseFloat(cs.opacity) > 0.5) {
      const f2 = fg.a < 1 ? blend(fg, bg.color) : fg;
      const L1 = lum(f2), L2 = lum(bg.color); const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
      const need = large ? 3 : minContrast;
      if (ratio < need) issues.push({ kind: 'contraste', text: txt, ratio: +ratio.toFixed(2), need });
    }
  }
  // contenedores que desbordan
  const boxes = Array.from(sl.querySelectorAll('.inner, .content, .panel, .card, .col, .box, .fact, .step, .tl-item, .quiz-opt, .cycle-text, figure, .stat'));
  for (const b of boxes) {
    const cs = getComputedStyle(b);
    if (b.scrollHeight > b.clientHeight + 4 && cs.overflowY !== 'visible' || b.scrollHeight > b.clientHeight + 4 && b.classList.contains('inner'))
      issues.push({ kind: 'desborde', where: b.className.split(' ')[0], text: (b.textContent || '').trim().slice(0, 50), over: b.scrollHeight - b.clientHeight });
    if (b.scrollWidth > b.clientWidth + 4 && cs.overflowX !== 'visible')
      issues.push({ kind: 'desborde-horizontal', where: b.className.split(' ')[0], text: (b.textContent || '').trim().slice(0, 50) });
  }
  return { id: sl.dataset.id, title: sl.dataset.title, issues };
}
"""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="QA visual y técnico de una presentación HTML")
    ap.add_argument("deck", type=Path)
    ap.add_argument("--out", type=Path, help="Carpeta de salida (por defecto <carpeta del deck>/qa)")
    ap.add_argument("--min-contrast", type=float, default=4.5)
    ap.add_argument("--no-shots", action="store_true", help="No guardar capturas por slide")
    a = ap.parse_args()
    deck = a.deck.resolve()
    if not deck.exists():
        print(f"No existe {deck}")
        return 1
    out = (a.out or deck.parent / "qa").resolve()
    out.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Falta Playwright: python -m pip install playwright && python -m playwright install chromium")
        return 1

    report = {"file": str(deck), "sizeMB": round(deck.stat().st_size / 1024 / 1024, 2), "external": [], "console": [], "fonts": [], "slides": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)

        def route(r):
            u = r.request.url
            if u.startswith(("file:", "data:", "blob:", "about:")):
                return r.continue_()
            report["external"].append(u)
            return r.abort()

        page.route("**/*", route)
        page.on("console", lambda m: report["console"].append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: report["console"].append(f"pageerror: {e}"))
        page.goto(deck.as_uri())
        page.wait_for_function("window.Deck && document.fonts && document.fonts.status === 'loaded'", timeout=20000)
        report["fonts"] = page.evaluate("Array.from(document.fonts).filter(f=>f.status==='loaded').map(f=>f.family+' '+f.style)")
        page.evaluate("document.documentElement.classList.add('no-anim'); document.body.classList.add('idle')")
        n = page.evaluate("Deck.count")
        shots = []
        for i in range(n):
            page.evaluate(f"Deck.goto({i}, {{all:true}})")
            page.wait_for_timeout(120)
            res = page.evaluate(CHECK_JS, a.min_contrast)
            res["index"] = i + 1
            report["slides"].append(res)
            shot = out / f"slide-{i + 1:02d}.png"
            page.screenshot(path=str(shot))
            shots.append(shot)
        browser.close()

    # hoja de contacto
    try:
        from PIL import Image, ImageDraw
        cols, tw, th = 4, 480, 270
        rows = (len(shots) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * (th + 34) + 16), (24, 26, 32))
        d = ImageDraw.Draw(sheet)
        try:
            from PIL import ImageFont
            fp = Path(__file__).resolve().parent.parent / 'assets' / 'fonts' / 'inter.woff2'
            font = ImageFont.truetype(str(fp), 16) if fp.exists() else ImageFont.load_default(size=16)
        except Exception:  # noqa: BLE001
            font = None
        for k, sp in enumerate(shots):
            im = Image.open(sp).convert("RGB").resize((tw, th), Image.LANCZOS)
            x = 16 + (k % cols) * (tw + 16)
            y = 16 + (k // cols) * (th + 34)
            sheet.paste(im, (x, y))
            d.text((x, y + th + 6), f"{k + 1}. {report['slides'][k]['title'][:58]}", fill=(220, 222, 230), font=font)
        sheet.save(out / "contact-sheet.png")
    except Exception as e:  # noqa: BLE001
        print("No se pudo crear la hoja de contacto:", e)
    if a.no_shots:
        for sp in shots:
            sp.unlink(missing_ok=True)

    errors = 0
    lines = []
    for s in report["slides"]:
        for it in s["issues"]:
            sev = "ERROR" if it["kind"] in ("desborde", "fuera-del-lienzo", "desborde-horizontal") or (it["kind"] == "contraste" and it["ratio"] < 3) else "AVISO"
            if sev == "ERROR":
                errors += 1
            lines.append(f"{sev}  slide {s['index']:>2} · {it['kind']} · {it.get('text', '')!r} " + " ".join(f"{k}={v}" for k, v in it.items() if k not in ("kind", "text")))
    real_console = [c for c in report["console"] if "favicon" not in c]
    if report["external"]:
        errors += 1
        lines.append(f"ERROR  requests externas ({len(report['external'])}): {report['external'][:3]}")
    if any(c.startswith(("error", "pageerror")) for c in real_console):
        errors += 1
        lines.append("ERROR  consola: " + " | ".join(real_console[:5]))
    if report["sizeMB"] > 10:
        errors += 1
        lines.append(f"ERROR  peso {report['sizeMB']} MB > 10 MB")
    report["errors"] = errors
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"QA {deck.name}: {len(report['slides'])} slides · {report['sizeMB']} MB · fuentes {len(report['fonts'])} · externas {len(report['external'])}")
    for ln in lines:
        print(ln)
    print(f"Hoja de contacto: {out / 'contact-sheet.png'}")
    print("RESULTADO:", "OK" if errors == 0 else f"{errors} error(es) por corregir")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
