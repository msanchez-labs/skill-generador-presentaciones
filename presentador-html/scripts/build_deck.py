#!/usr/bin/env python3
"""
build_deck.py — Convierte un deck.json en una presentación HTML única (offline).

Uso:
    python scripts/build_deck.py <ruta/deck.json> [--out salida.html] [--no-images-opt]

- Todas las rutas de imágenes/SVG del deck.json son RELATIVAS a la carpeta del deck.json.
- Los recursos (motor, temas, fuentes, íconos) se buscan RELATIVOS a este script,
  así la skill funciona en cualquier carpeta donde se copie (Windows, macOS, Linux).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

VERSION = "1.0.0"
SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
ENGINE = ASSETS / "engine"

FONT_META = {
    "inter": ("Inter", "100 900", "normal", "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"),
    "space-grotesk": ("Space Grotesk", "300 700", "normal", "system-ui, 'Segoe UI', sans-serif"),
    "instrument-serif": ("Instrument Serif", "400", "normal", "Georgia, 'Times New Roman', serif"),
    "plus-jakarta-sans": ("Plus Jakarta Sans", "200 800", "normal", "system-ui, 'Segoe UI', sans-serif"),
    "sora": ("Sora", "100 800", "normal", "system-ui, 'Segoe UI', sans-serif"),
    "jetbrains-mono": ("JetBrains Mono", "100 800", "normal", "ui-monospace, Menlo, Consolas, monospace"),
}
TONE_MAX_WORDS = {"storytelling": 25, "directo": 35, "explicativo": 50, "minimalista": 10, "grafico": 12,
                  "datos": 30, "consultor": 60, "inspiracional": 15, "ludico": 25, "tecnico": 60}
TYPES = ["title", "section", "agenda", "statement", "big-number", "split", "image-full", "gallery", "cards",
         "process", "timeline", "comparison", "chart", "quote", "cycle", "status", "quiz", "diagram", "cta",
         "closing", "html"]

WARN: list[str] = []


def warn(msg: str) -> None:
    WARN.append(msg)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- texto
def md_inline(s) -> str:
    """Escapa HTML y aplica markdown mínimo: **negrita**, *itálica*, ==resaltado==, [texto](url), saltos."""
    if s is None:
        return ""
    t = html.escape(str(s), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"==(.+?)==", r'<mark class="hl">\1</mark>', t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = t.replace("\n", "<br>")
    return t


def words(*parts) -> int:
    n = 0
    for p in parts:
        if not p:
            continue
        if isinstance(p, (list, tuple)):
            n += words(*p)
        elif isinstance(p, dict):
            n += words(*[v for k, v in p.items() if k in ("title", "text", "label", "note")])
        else:
            n += len(re.findall(r"\w+", str(p)))
    return n


def fmt_num(v: float, dec: int, lang: str) -> str:
    s = f"{v:,.{dec}f}"
    if lang.startswith(("es", "pt", "de", "it", "fr")):
        s = s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")
        if lang.startswith("fr"):
            s = s.replace(".", " ")
    return s


def slugify(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s.lower(), flags=re.U)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:60] or "deck"


# --------------------------------------------------------------------------- íconos
class Icons:
    def __init__(self) -> None:
        self.data = json.loads(read_text(ASSETS / "icons.json"))

    def svg(self, name: str, cls: str = "i") -> str:
        if not name:
            return ""
        inner = self.data.get(name)
        if inner is None:
            warn(f"Ícono no encontrado: '{name}' (se usa 'circle-help'). Ver assets/icons.json")
            inner = self.data.get("circle-help", "")
        return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{inner}</svg>'


# --------------------------------------------------------------------------- imágenes
class Images:
    """Incrusta imágenes como clases CSS deduplicadas (.img-N { background-image: url(data:…) })."""

    def __init__(self, base: Path, optimize: bool = True) -> None:
        self.base = base
        self.optimize = optimize
        self.cache: dict[str, str] = {}
        self.css: list[str] = []
        self.bytes = 0

    def _load(self, src: str) -> tuple[bytes, str]:
        if re.match(r"^https?://", src):
            cache_dir = self.base / ".cache"
            cache_dir.mkdir(exist_ok=True)
            name = hashlib.sha1(src.encode()).hexdigest()[:16] + Path(src.split("?")[0]).suffix[:5]
            fp = cache_dir / name
            if not fp.exists():
                req = urllib.request.Request(src, headers={"User-Agent": "presentador-html/1.0"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    fp.write_bytes(r.read())
            path = fp
        else:
            path = (self.base / src).resolve()
        if not path.exists():
            raise FileNotFoundError(src)
        return path.read_bytes(), path.suffix.lower()

    def data_uri(self, src: str, max_w: int = 1920, max_h: int = 1080) -> str:
        raw, ext = self._load(src)
        if ext == ".svg":
            return "data:image/svg+xml;base64," + base64.b64encode(raw).decode()
        if not self.optimize:
            mime = {".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}.get(ext, "image/jpeg")
            return f"data:{mime};base64," + base64.b64encode(raw).decode()
        try:
            from PIL import Image, ImageOps
        except ImportError:
            warn("Pillow no instalado: imágenes sin optimizar (python -m pip install Pillow)")
            mime = {".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
            return f"data:{mime};base64," + base64.b64encode(raw).decode()
        im = Image.open(io.BytesIO(raw))
        im = ImageOps.exif_transpose(im)
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        im = im.convert("RGBA" if has_alpha else "RGB")
        w, h = im.size
        ratio = min(1.0, max(max_w / w, max_h / h))  # cubrir el área destino sin agrandar
        if ratio < 1.0:
            im = im.resize((max(1, round(w * ratio)), max(1, round(h * ratio))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=78, method=5)
        return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

    def cls(self, src: str, max_w: int = 1920, max_h: int = 1080) -> str:
        key = f"{src}|{max_w}x{max_h}"
        if key in self.cache:
            return self.cache[key]
        try:
            uri = self.data_uri(src, max_w, max_h)
        except Exception as e:  # noqa: BLE001
            warn(f"Imagen no disponible '{src}': {e}")
            self.cache[key] = "img-missing"
            return "img-missing"
        name = f"img-{len(self.cache) + 1}"
        self.cache[key] = name
        self.bytes += len(uri)
        self.css.append(f'.{name}{{background-image:url("{uri}")}}')
        return name


# --------------------------------------------------------------------------- render
class Renderer:
    def __init__(self, deck: dict, base: Path, optimize: bool) -> None:
        self.deck = deck
        self.meta = deck.get("meta", {})
        self.lang = self.meta.get("lang", "es")
        self.icons = Icons()
        self.images = Images(base, optimize)
        self.base = base
        self.i = 0  # contador de animación por slide
        self.frag = False

    # helpers ---------------------------------------------------------------
    def a(self, extra: str = "") -> str:
        self.i += 1
        cls = ("frag " if self.frag else "rise ") + extra
        style = "" if self.frag else f' style="--i:{self.i}"'
        return f' class="{cls.strip()}"{style}'

    def a_static(self, extra: str = "") -> str:
        """Siempre animación automática (títulos), nunca fragmento."""
        self.i += 1
        return f' class="{("rise " + extra).strip()}" style="--i:{self.i}"'

    def ph(self, img, extra: str = "", max_w: int = 1920, max_h: int = 1080) -> str:
        if not img:
            return ""
        if isinstance(img, str):
            img = {"src": img}
        c = self.images.cls(img["src"], max_w, max_h)
        style = []
        if img.get("position"):
            style.append(f"background-position:{img['position']}")
        st = f' style="{";".join(style)}"' if style else ""
        alt = html.escape(img.get("alt", ""), quote=True)
        role = f' role="img" aria-label="{alt}"' if alt else ' aria-hidden="true"'
        fit = " contain" if img.get("fit") == "contain" else ""
        credit = f'<span class="credit">{md_inline(img["credit"])}</span>' if img.get("credit") else ""
        return f'<div class="ph {c}{fit} {extra}"{st}{role}>{credit}</div>'

    def eyebrow(self, s) -> str:
        return f'<p{self.a_static("eyebrow")} data-edit>{md_inline(s.get("eyebrow"))}</p>' if s.get("eyebrow") else ""

    def title(self, s, tag="h2", key="title", extra="") -> str:
        t = s.get(key)
        return f'<{tag}{self.a_static("title " + extra)} data-edit>{md_inline(t)}</{tag}>' if t else ""

    def lead(self, s, key="subtitle") -> str:
        t = s.get(key) or (s.get("lead") if key == "subtitle" else None)
        return f'<p{self.a_static("subtitle")} data-edit>{md_inline(t)}</p>' if t else ""

    def chips(self, s) -> str:
        if not s.get("chips"):
            return ""
        out = []
        for ch in s["chips"]:
            if isinstance(ch, str):
                ch = {"text": ch}
            out.append(f'<span class="chip">{self.icons.svg(ch.get("icon", ""))}<span data-edit>{md_inline(ch["text"])}</span></span>')
        return f'<div{self.a_static("chips")}>{"".join(out)}</div>'

    def bullets(self, items, extra="") -> str:
        if not items:
            return ""
        lis = "".join(f'<li{self.a()} data-edit>{md_inline(x)}</li>' for x in items)
        return f'<ul class="bullets {extra}">{lis}</ul>'

    def facts(self, items) -> str:
        if not items:
            return ""
        out = []
        for f in items:
            out.append(f'<div{self.a("fact")}><div class="fact-icon">{self.icons.svg(f.get("icon", "circle"))}</div>'
                       f'<div><strong data-edit>{md_inline(f.get("title"))}</strong>'
                       f'{"<span data-edit>" + md_inline(f.get("text")) + "</span>" if f.get("text") else ""}</div></div>')
        return f'<div class="facts">{"".join(out)}</div>'

    def text(self, s) -> str:
        t = s.get("text")
        if not t:
            return ""
        paras = t if isinstance(t, list) else [t]
        return '<div class="body">' + "".join(f'<p{self.a()} data-edit>{md_inline(p)}</p>' for p in paras) + "</div>"

    def source(self, s) -> str:
        return f'<p class="source" data-edit>{md_inline(s["source"])}</p>' if s.get("source") else ""

    def figure(self, s) -> str:
        f = s.get("figure")
        if not f:
            return ""
        if isinstance(f, str):
            f = {"src": f}
        size = int(f.get("size", 200))
        shape = " round" if f.get("shape") == "circle" else ""
        self.i += 1
        return (f'<div class="rise figure{shape}" style="--fig:{size}px;--i:{self.i}">'
                f'{self.ph(dict(f, fit=f.get("fit", "contain"), credit=None), "", size * 2, size * 2)}</div>')

    def content_block(self, s) -> str:
        return (self.figure(s) + self.eyebrow(s) + self.chips(s) + self.title(s) + self.lead(s) + self.text(s)
                + self.bullets(s.get("bullets")) + self.facts(s.get("facts")) + self.source(s))

    # tipos -------------------------------------------------------------------
    def r_title(self, s):
        meta = s.get("meta") or [x for x in [self.meta.get("author"), self.meta.get("date")] if x]
        meta_html = f'<div{self.a_static("meta")}>' + "".join(f"<span data-edit>{md_inline(m)}</span>" for m in meta) + "</div>" if meta else ""
        return self.eyebrow(s) + self.chips(s) + self.title(s, "h1") + self.lead(s) + meta_html

    def r_closing(self, s):
        return self.eyebrow(s) + self.title(s, "h2", extra="") + self.lead(s) + self.bullets(s.get("bullets")) + (
            f'<p{self.a_static("subtitle")} data-edit>{md_inline(s["contact"])}</p>' if s.get("contact") else "")

    def r_section(self, s):
        num = s.get("number", "")
        return (f'<div{self.a_static("sec-num")}>{html.escape(str(num))}</div>' if num != "" else "") + self.title(s) + self.lead(s)

    def r_agenda(self, s):
        cur = s.get("current", -1)
        lis = "".join(f'<li{self.a("current" if k == cur else "")} data-edit>{md_inline(x)}</li>' for k, x in enumerate(s.get("items", [])))
        return self.eyebrow(s) + self.title(s) + f'<ol class="agenda">{lis}</ol>'

    def r_statement(self, s):
        return self.eyebrow(s) + self.title(s) + self.lead(s)

    def r_big_number(self, s):
        stats = s.get("stats", [])
        out = []
        for st in stats:
            v = st.get("value", 0)
            dec = int(st.get("decimals", 0 if float(v).is_integer() else 1))
            num = f'<span class="num tabular" data-countup="{v}" data-decimals="{dec}">{fmt_num(float(v), dec, self.lang)}</span>'
            pre = html.escape(st.get("prefix", ""))
            unit = f'<span class="unit">{html.escape(st["unit"])}</span>' if st.get("unit") else ""
            out.append(f'<div{self.a("stat")}><div class="stat-value">{pre}{num}{unit}</div>'
                       f'<div class="stat-label" data-edit>{md_inline(st.get("label"))}</div>'
                       + (f'<div class="stat-note" data-edit>{md_inline(st.get("note"))}</div>' if st.get("note") else "") + "</div>")
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="stats" style="--n:{len(stats)}">{"".join(out)}</div>' + self.source(s)

    def r_split(self, s):
        media = self.ph(s.get("image"), "", 1400, 1080)
        return f'<div class="media">{media}</div><div class="content">{self.content_block(s)}</div>'

    def r_image_full(self, s):
        return f'<div class="panel">{self.content_block(s)}</div>'

    def r_gallery(self, s):
        imgs = s.get("images", [])
        figs = []
        for im in imgs:
            cap = ""
            if im.get("title") or im.get("text"):
                cap = f'<figcaption><strong data-edit>{md_inline(im.get("title"))}</strong><span data-edit>{md_inline(im.get("text"))}</span></figcaption>'
            figs.append(f'<figure{self.a()}>{self.ph(im, "", 1100, 900)}{cap}</figure>')
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="gallery" style="--n:{len(imgs)}">{"".join(figs)}</div>'

    def r_cards(self, s):
        items = s.get("items", [])
        cols = s.get("cols") or (3 if len(items) in (3, 5, 6) else 2 if len(items) in (2, 4) else 3)
        out = []
        for it in items:
            img = self.ph(it.get("image"), "", 900, 600) if it.get("image") else ""
            ic = f'<div class="card-icon">{self.icons.svg(it["icon"])}</div>' if it.get("icon") and not img else ""
            out.append(f'<div{self.a("card" + (" featured" if it.get("featured") else ""))}>{img}{ic}'
                       f'<h3 data-edit>{md_inline(it.get("title"))}</h3><p data-edit>{md_inline(it.get("text"))}</p></div>')
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="cards" style="--cols:{cols}">{"".join(out)}</div>'

    def r_process(self, s):
        steps = s.get("steps", [])
        cur = s.get("current", -1)
        out = []
        for k, st in enumerate(steps):
            ic = self.icons.svg(st["icon"]) if st.get("icon") else ""
            out.append(f'<li{self.a("step" + (" current" if k == cur else ""))}><div class="step-num">{k + 1:02d}{ic}</div>'
                       f'<h3 data-edit>{md_inline(st.get("title"))}</h3><p data-edit>{md_inline(st.get("text"))}</p></li>')
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<ol class="process" style="--n:{len(steps)}">{"".join(out)}</ol>'

    def r_timeline(self, s):
        items = s.get("items", [])
        out = []
        for it in items:
            out.append(f'<div{self.a("tl-item" + (" current" if it.get("current") else ""))}><div class="tl-date" data-edit>{md_inline(it.get("date"))}</div>'
                       f'<h3 data-edit>{md_inline(it.get("title"))}</h3><p data-edit>{md_inline(it.get("text"))}</p></div>')
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="timeline" style="--n:{len(items)}">{"".join(out)}</div>'

    def r_comparison(self, s):
        cols = s.get("columns", [])
        out = []
        for c in cols:
            img = self.ph(c.get("image"), "", 1000, 600) if c.get("image") else ""
            badge = f'<span class="badge">{md_inline(c.get("badge") or "Recomendado")}</span>' if c.get("recommended") or c.get("badge") else ""
            sub = f'<p class="col-sub" data-edit>{md_inline(c["subtitle"])}</p>' if c.get("subtitle") else ""
            out.append(f'<div{self.a("col" + (" recommended" if c.get("recommended") else ""))}>{img}{badge}'
                       f'<h3 data-edit>{md_inline(c.get("title"))}</h3>{sub}{self.bullets(c.get("bullets"))}</div>')
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="compare" style="--n:{len(cols)}">{"".join(out)}</div>' + self.source(s)

    def r_chart(self, s):
        ch = s.get("chart", {})
        svg = chart_svg(ch, self.lang)
        insight = f'<div class="insight" data-edit>{md_inline(s["insight"])}</div>' if s.get("insight") else ""
        return (self.eyebrow(s) + self.title(s) + self.lead(s)
                + f'<div class="chart-row"><div class="chart-wrap rise" style="--i:3">{svg}</div>{insight}</div>' + self.source(s))

    def r_quote(self, s):
        return (f'<blockquote{self.a_static()}><p data-edit>{md_inline(s.get("text"))}</p>'
                f'<cite data-edit>{md_inline(s.get("author"))}</cite></blockquote>')

    def r_cycle(self, s):
        items = s.get("items", [])
        n = max(1, len(items))
        R = s.get("radius", 330)
        size = s.get("nodeSize", 120 if n <= 8 else 96)
        cur = s.get("current", -1)
        nodes = []
        for k, it in enumerate(items):
            ang = -math.pi / 2 + 2 * math.pi * k / n
            x, y = R * math.cos(ang), R * math.sin(ang)
            vis = self.ph(it["image"], "", 400, 400) if it.get("image") else f'<div class="node-icon">{self.icons.svg(it.get("icon", "circle"))}</div>'
            nodes.append(f'<div class="node{" current" if k == cur else ""} {"frag" if self.frag else "rise"}" style="left:calc(50% + {x:.0f}px);top:calc(50% + {y:.0f}px);--i:{k + 2}">{vis}<span data-edit>{md_inline(it.get("label"))}</span></div>')
        center = s.get("center") or {}
        c_html = (f'<div class="center" style="left:50%;top:50%"><strong data-edit>{md_inline(center.get("title"))}</strong>'
                  f'<span data-edit>{md_inline(center.get("text"))}</span></div>') if center else ""
        ring = f'<div class="ring" style="left:calc(50% - {R}px);top:calc(50% - {R}px);width:{2 * R}px;height:{2 * R}px"></div>'
        left = f'<div class="cycle-text">{self.content_block(s)}</div>'
        return left + f'<div class="cycle" style="--node-size:{size}px">{ring}{c_html}{"".join(nodes)}</div>'

    def r_status(self, s):
        h = s.get("health", {"status": "g", "label": "En plan"})
        rag = lambda r: {"g": "rag-g", "a": "rag-a", "r": "rag-r"}.get(str(r)[:1].lower(), "rag-g")
        rag_lbl = lambda r: {"g": "Verde", "a": "Ámbar", "r": "Rojo"}.get(str(r)[:1].lower(), "Verde")
        trend = {"up": "↑", "down": "↓", "flat": "→"}
        rows = "".join(f'<tr><td data-edit>{md_inline(m.get("name"))}</td><td class="v" data-edit>{md_inline(m.get("value"))}</td>'
                       f'<td><span class="rag {rag(m.get("rag", "g"))}"><span class="dot"></span>{rag_lbl(m.get("rag", "g"))}</span></td>'
                       f'<td class="trend" title="Tendencia">{trend.get(m.get("trend", ""), "")}</td></tr>' for m in s.get("metrics", []))
        lst = lambda items: "<ul>" + "".join(f"<li data-edit>{md_inline(x)}</li>" for x in (items or [])) + "</ul>"
        period = f'<div class="period" data-edit>{md_inline(s.get("period"))}</div>' if s.get("period") else ""
        head = (f'<div class="status-head"><div>{self.eyebrow(s)}{self.title(s)}{period}</div>'
                f'<div class="health {rag(h.get("status"))}"><span class="dot"></span><span data-edit>{md_inline(h.get("label"))}</span></div></div>')
        dec = s.get("decision") or "Solo informativo: no se requieren decisiones."
        grid = (f'<div class="status-grid">'
                f'<div class="box metrics rise" style="--i:3"><h3>Métricas clave</h3><table>{rows}</table></div>'
                f'<div class="box rise" style="--i:4"><h3>Logros</h3>{lst(s.get("done"))}</div>'
                f'<div class="box rise" style="--i:5"><h3>Próximos pasos</h3>{lst(s.get("next"))}</div>'
                f'<div class="box rise" style="--i:6"><h3>Riesgos y problemas</h3>{lst(s.get("risks"))}</div>'
                f'<div class="box decision rise" style="--i:7"><h3>Decisión requerida</h3><p data-edit>{md_inline(dec)}</p></div></div>')
        return head + grid

    def r_quiz(self, s):
        ops = s.get("options", [])
        letters = "ABCDEF"
        lis = "".join(f'<li{self.a()}><button class="quiz-opt" type="button" data-correct="{1 if o.get("correct") else 0}">'
                      f'<span class="letter">{letters[k]}</span><span data-edit>{md_inline(o.get("text"))}</span></button></li>' for k, o in enumerate(ops))
        fb = f'<div class="quiz-feedback" data-edit>{md_inline(s.get("explanation"))}</div>' if s.get("explanation") else ""
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<ol class="quiz-options">{lis}</ol>' + fb

    def r_diagram(self, s):
        d = s.get("svg")
        body = ""
        if d:
            if d.strip().startswith("<svg"):
                body = d
            else:
                p = (self.base / d)
                if p.exists():
                    body = read_text(p)
                    body = re.sub(r"<\?xml[^>]*\?>", "", body)
                else:
                    warn(f"SVG de diagrama no encontrado: {d}")
        elif s.get("image"):
            body = self.ph(dict(s["image"], fit="contain"), "", 1800, 900)
        cap = self.source(s)
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<div class="diagram rise" style="--i:3">{body}</div>' + cap

    def r_cta(self, s):
        acts = "".join(f'<li{self.a()}><span class="ai">{self.icons.svg(x.get("icon", "arrow-right"))}</span><span data-edit>{md_inline(x.get("text"))}</span></li>'
                       for x in s.get("actions", []))
        return self.eyebrow(s) + self.title(s) + self.lead(s) + f'<ul class="actions">{acts}</ul>'

    def r_html(self, s):
        return s.get("html", "")

    # slide -------------------------------------------------------------------
    def slide(self, s: dict, idx: int) -> str:
        t = s.get("type", "split")
        if t not in TYPES:
            warn(f"Slide {idx + 1}: tipo desconocido '{t}', se usa 'split'")
            t = "split"
        self.i = 0
        self.frag = bool(s.get("fragments", self.meta.get("fragments", False)))
        sid = s.get("id") or f"s{idx + 1}"
        classes = ["slide", f"t-{t}"]
        bg_html = ""
        bg = s.get("background")
        if t in ("image-full",) and not bg and s.get("image"):
            bg = {"image": s["image"]}
        if t in ("title", "closing", "quote", "statement") and not bg and s.get("image"):
            bg = {"image": s["image"]}
        if bg:
            img = bg.get("image")
            if img:
                if isinstance(img, str):
                    img = {"src": img}
                c = self.images.cls(img["src"])
                pos = f' style="background-position:{img["position"]}"' if img.get("position") else ""
                kb = " kenburns" if bg.get("kenburns", s.get("kenburns", True)) else ""
                alt = html.escape(img.get("alt", ""), quote=True)
                role = f' role="img" aria-label="{alt}"' if alt else ' aria-hidden="true"'
                bg_html += f'<div class="bg {c}{kb}"{pos}{role}></div>'
                ov = bg.get("overlay", "left" if t == "image-full" and s.get("panel") == "left" else "bottom")
                if ov != "none":
                    bg_html += f'<div class="bg-overlay {"left" if ov == "left" else ""}"></div>'
                if img.get("credit"):
                    bg_html += f'<span class="credit">{md_inline(img["credit"])}</span>'
                classes.append("has-bg")
            if bg.get("grain"):
                bg_html += '<div class="grain"></div>'
            if bg.get("aurora"):
                bg_html += '<div class="aurora"></div>'
        elif self.meta.get("aurora") and t in ("title", "statement", "closing", "big-number", "cta"):
            bg_html += '<div class="aurora"></div>'
        if t == "split":
            if s.get("side", "left") == "right":
                classes.append("media-right")
            if s.get("bleed"):
                classes.append("bleed")
            if s.get("wide"):
                classes.append("wide-media")
        if t == "image-full" and s.get("panel") == "left":
            classes.append("left-panel")
        if s.get("align") == "center":
            classes.append("center")
        if s.get("class"):
            classes.append(str(s["class"]))
        inner = getattr(self, "r_" + t.replace("-", "_"))(s)
        notes = s.get("notes")
        notes_html = ""
        if notes:
            paras = notes if isinstance(notes, list) else [notes]
            notes_html = '<aside class="notes" hidden>' + "".join(f"<p>{md_inline(p)}</p>" for p in paras) + "</aside>"
        attrs = [f'data-id="{html.escape(sid)}"', f'data-index="{idx + 1}"']
        title_plain = re.sub(r"[*=_`]", "", str(s.get("title") or s.get("text") or t))
        attrs.append(f'data-title="{html.escape(title_plain, quote=True)}"')
        if s.get("timing"):
            attrs.append(f'data-timing="{int(s["timing"])}"')
        if s.get("sfx"):
            attrs.append(f'data-sfx="{html.escape(s["sfx"])}"')
        extra = ""
        if t == "big-number":
            extra = f' data-n="{len(s.get("stats", []))}"'
        # presupuesto de palabras por tono
        tone = s.get("tone", self.meta.get("tone"))
        limit = TONE_MAX_WORDS.get(tone or "", 0)
        if limit and t not in ("status", "html", "quiz", "comparison"):
            wc = words(s.get("title"), s.get("subtitle"), s.get("lead"), s.get("text"), s.get("bullets"), s.get("facts"), s.get("items"))
            if wc > limit * 1.6:
                warn(f"Slide {idx + 1} ('{title_plain[:40]}'): {wc} palabras; el tono '{tone}' sugiere ≤ {limit}")
        return (f'<section class="{" ".join(classes)}" {" ".join(attrs)}{extra} aria-roledescription="slide" aria-label="{idx + 1}: {html.escape(title_plain, quote=True)}">'
                f'{bg_html}<div class="inner">{inner}</div>{notes_html}</section>')


# --------------------------------------------------------------------------- gráficos SVG
def chart_svg(ch: dict, lang: str) -> str:
    kind = ch.get("kind", "bar")
    labels = ch.get("labels", [])
    values = [float(v) for v in ch.get("values", [])]
    if not values:
        return ""
    hi = ch.get("highlight", [])
    hi = set(hi if isinstance(hi, list) else [hi])
    unit = ch.get("unit", "")
    dec = int(ch.get("decimals", 0))
    vmax = float(ch.get("max", max(values) * 1.12 or 1))
    f = lambda v: fmt_num(v, dec, lang) + unit
    Wd, Hd = 1000, 560
    out = [f'<svg class="chart" viewBox="0 0 {Wd} {Hd}" role="img" aria-label="{html.escape(ch.get("alt", "Gráfico"))}">']
    if kind == "hbar":
        n = len(values); top = 10; rowh = (Hd - top) / n; lw = 300
        for k, (lab, v) in enumerate(zip(labels, values)):
            y = top + k * rowh; bw = (Wd - lw - 120) * v / vmax; c = "bar hi" if k in hi else "bar"
            out.append(f'<text x="{lw - 16}" y="{y + rowh / 2 + 9:.0f}" text-anchor="end" font-size="26">{html.escape(str(lab))}</text>')
            out.append(f'<rect class="{c}" x="{lw}" y="{y + rowh * 0.18:.0f}" width="{bw:.0f}" height="{rowh * 0.64:.0f}" rx="6"/>')
            out.append(f'<text class="val" x="{lw + bw + 12:.0f}" y="{y + rowh / 2 + 9:.0f}" font-size="26">{f(v)}</text>')
    elif kind == "line":
        n = len(values); l, r, t, b = 40, 40, 40, 70
        xs = [l + (Wd - l - r) * k / max(1, n - 1) for k in range(n)]
        ys = [Hd - b - (Hd - t - b) * v / vmax for v in values]
        out.append(f'<line class="axis" x1="{l}" y1="{Hd - b}" x2="{Wd - r}" y2="{Hd - b}"/>')
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs, ys))
        out.append(f'<polyline class="line hi" points="{pts}"/>')
        for k, (x, y) in enumerate(zip(xs, ys)):
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{9 if k in hi else 6}" fill="var(--{"accent" if k in hi else "muted"})"/>')
            if k in hi or n <= 8:
                out.append(f'<text class="val" x="{x:.0f}" y="{y - 18:.0f}" text-anchor="middle" font-size="24">{f(values[k])}</text>')
            if k < len(labels):
                out.append(f'<text x="{x:.0f}" y="{Hd - b + 40}" text-anchor="middle" font-size="22">{html.escape(str(labels[k]))}</text>')
    else:
        n = len(values); l, r, t, b = 20, 20, 50, 70
        slot = (Wd - l - r) / n; bw = slot * 0.62
        out.append(f'<line class="axis" x1="{l}" y1="{Hd - b}" x2="{Wd - r}" y2="{Hd - b}"/>')
        for k, v in enumerate(values):
            x = l + slot * k + (slot - bw) / 2; h = (Hd - t - b) * v / vmax; y = Hd - b - h
            c = "bar hi" if k in hi else "bar"
            out.append(f'<rect class="{c}" x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="6"/>')
            out.append(f'<text class="val" x="{x + bw / 2:.0f}" y="{y - 14:.0f}" text-anchor="middle" font-size="26">{f(v)}</text>')
            if k < len(labels):
                out.append(f'<text x="{x + bw / 2:.0f}" y="{Hd - b + 40}" text-anchor="middle" font-size="24">{html.escape(str(labels[k]))}</text>')
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- tema y fuentes
def load_theme(meta: dict, base: Path) -> tuple[str, dict]:
    th = meta.get("theme", "editorial-claro")
    if isinstance(th, dict):
        name, theme = "custom", th
    else:
        p = Path(th)
        cand = [base / th, ASSETS / "themes" / f"{th}.json"]
        f = next((c for c in cand if c.suffix == ".json" and c.exists()), None)
        if not f:
            warn(f"Tema '{th}' no encontrado; se usa editorial-claro")
            f = ASSETS / "themes" / "editorial-claro.json"
        name, theme = f.stem, json.loads(read_text(f))
    ov = meta.get("themeOverrides") or {}
    theme = json.loads(json.dumps(theme))
    for k, v in ov.items():
        if isinstance(v, dict):
            theme.setdefault(k, {}).update(v)
        else:
            theme[k] = v
    return name, theme


def fonts_css(theme: dict) -> str:
    used = {theme["fonts"].get("display", "inter"), theme["fonts"].get("body", "inter"), theme["fonts"].get("mono", "jetbrains-mono")}
    css = []
    for key in sorted(used):
        if key not in FONT_META:
            warn(f"Fuente '{key}' no incluida; se usa la pila del sistema")
            continue
        fam, wght, style, _ = FONT_META[key]
        f = ASSETS / "fonts" / f"{key}.woff2"
        if f.exists():
            b64 = base64.b64encode(f.read_bytes()).decode()
            css.append(f'@font-face{{font-family:"{fam}";font-style:{style};font-weight:{wght};font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
        fi = ASSETS / "fonts" / f"{key}-italic.woff2"
        if fi.exists():
            b64 = base64.b64encode(fi.read_bytes()).decode()
            css.append(f'@font-face{{font-family:"{fam}";font-style:italic;font-weight:{wght};font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
    return "\n".join(css)


def theme_css(theme: dict) -> str:
    c = theme["colors"]
    fam = lambda k: (f'"{FONT_META[k][0]}", {FONT_META[k][3]}' if k in FONT_META else "system-ui, sans-serif")
    v = [f"--{re.sub(r'(?<!^)(?=[A-Z])', '-', k).lower()}:{val}" for k, val in c.items()]
    v += [f"--font-display:{fam(theme['fonts'].get('display', 'inter'))}", f"--font-body:{fam(theme['fonts'].get('body', 'inter'))}",
          f"--font-mono:{fam(theme['fonts'].get('mono', 'jetbrains-mono'))}", f"--radius:{theme.get('radius', '14px')}",
          f"--display-weight:{theme.get('displayWeight', 700)}", f"--title-scale:{theme.get('titleScale', 1)}", f"--display-tracking:{theme.get('displayTracking', '-0.02em')}"]
    return ":root{" + ";".join(v) + "}\nbody.idle{cursor:none}"


# --------------------------------------------------------------------------- build
def build(deck_path: Path, out: Path | None, optimize: bool = True) -> Path:
    deck = json.loads(read_text(deck_path))
    base = deck_path.parent
    meta = deck.setdefault("meta", {})
    slides = deck.get("slides", [])
    if not slides:
        raise SystemExit("El deck no tiene slides.")
    theme_name, theme = load_theme(meta, base)
    r = Renderer(deck, base, optimize)
    slides_html = "\n".join(r.slide(s, k) for k, s in enumerate(slides))
    icons = r.icons
    tpl = read_text(ENGINE / "template.html")
    tpl = re.sub(r"\{\{ICON:([\w-]+)\}\}", lambda m: icons.svg(m.group(1)), tpl)
    title = meta.get("title") or (slides[0].get("title") or "Presentación")
    title_plain = re.sub(r"[*=_`]", "", str(title))
    build_id = hashlib.sha1((json.dumps(deck, sort_keys=True, ensure_ascii=False) + VERSION).encode()).hexdigest()[:10]
    cfg = {
        "id": meta.get("id") or slugify(title_plain), "buildId": build_id, "title": title_plain, "lang": meta.get("lang", "es"),
        "author": meta.get("author", ""), "fileName": meta.get("fileName") or slugify(title_plain), "version": VERSION,
        "dimPrevious": bool(meta.get("dimPrevious", False)), "quizPoints": meta.get("quizPoints", 10),
        "autoplaySec": meta.get("autoplaySec", 8), "inkColors": meta.get("inkColors"),
        "uiIcons": {"soundOn": icons.svg("volume-2"), "soundOff": icons.svg("volume-x")},
    }
    cfg = {k: v for k, v in cfg.items() if v is not None}
    js_json = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    extra_css = meta.get("css", "")
    repl = {
        "{{LANG}}": html.escape(meta.get("lang", "es")), "{{THEME_NAME}}": theme_name, "{{THEME_MODE}}": theme.get("mode", "light"),
        "{{VERSION}}": VERSION, "{{TITLE}}": html.escape(title_plain), "{{FONTS_CSS}}": fonts_css(theme),
        "{{THEME_CSS}}": theme_css(theme), "{{ENGINE_CSS}}": read_text(ENGINE / "engine.css"), "{{IMAGES_CSS}}": "\n".join(r.images.css),
        "{{EXTRA_CSS}}": extra_css, "{{SLIDES}}": slides_html, "{{CONFIG}}": js_json(cfg), "{{STATE}}": "{}",
        "{{ENGINE_JS}}": read_text(ENGINE / "engine.js"),
    }
    out_html = tpl
    for k, v in repl.items():
        out_html = out_html.replace(k, v)
    out = out or (base / (meta.get("output") or "deck.html"))
    out.write_text(out_html, encoding="utf-8", newline="\n")
    size = out.stat().st_size
    print(f"OK  {out}  ·  {len(slides)} slides  ·  {size / 1024 / 1024:.2f} MB  ·  tema {theme_name}")
    if size > 10 * 1024 * 1024:
        warn(f"El archivo pesa {size / 1024 / 1024:.1f} MB (> 10 MB). Reduce imágenes.")
    elif size > 5 * 1024 * 1024:
        warn(f"El archivo pesa {size / 1024 / 1024:.1f} MB (> 5 MB recomendado).")
    for w in WARN:
        print("AVISO", w)
    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Construye una presentación HTML única desde deck.json")
    ap.add_argument("deck", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--no-images-opt", action="store_true", help="Incrustar imágenes sin recomprimir")
    a = ap.parse_args()
    build(a.deck.resolve(), a.out.resolve() if a.out else None, not a.no_images_opt)


if __name__ == "__main__":
    main()
