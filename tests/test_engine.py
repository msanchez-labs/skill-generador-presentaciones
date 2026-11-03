#!/usr/bin/env python3
"""
Pruebas funcionales del motor (sin pytest). Construye el deck demo y verifica en
Chromium, Firefox y WebKit (los que estén instalados) las capacidades clave.

Uso:  python tests/test_engine.py [--browsers chromium,firefox,webkit]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "presentador-html"
DECK_JSON = SKILL / "examples" / "demo-capacidades" / "deck.json"
DECK = DECK_JSON.with_name("deck.html")


def check(cond: bool, msg: str, fails: list[str]) -> None:
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def run(browser_name: str) -> list[str]:
    from playwright.sync_api import sync_playwright

    fails: list[str] = []
    print(f"[{browser_name}]")
    with sync_playwright() as p:
        try:
            browser = getattr(p, browser_name).launch()
        except Exception as e:  # noqa: BLE001
            print(f"  (omitido: {browser_name} no instalado: {str(e)[:80]})")
            return []
        ctx = browser.new_context(viewport={"width": 1600, "height": 900}, accept_downloads=True)
        page = ctx.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(DECK.as_uri())
        page.wait_for_function("window.Deck && Deck.count > 0")
        n = page.evaluate("Deck.count")
        check(n == 14, f"carga {n} slides", fails)

        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(1300)
        check(page.evaluate("Deck.index") == 1, "→ avanza a la slide 2", fails)
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(1300)
        check(page.evaluate("Deck.index") == 0, "← retrocede a la slide 1", fails)

        # fragmentos (slide 5 tiene 4 pasos)
        page.evaluate("Deck.goto(4)")
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(200)
        check(page.evaluate("Deck.step") == 1 and page.evaluate("Deck.index") == 4, "fragmento 1 visible sin cambiar de slide", fails)

        # ir a slide por número
        page.keyboard.type("3")
        page.keyboard.press("Enter")
        page.wait_for_timeout(1300)
        check(page.evaluate("Deck.index") == 2, "número + Enter salta a la slide 3", fails)

        # láser
        page.keyboard.press("l")
        check(page.evaluate("document.body.classList.contains('tool-laser')"), "L activa el láser", fails)
        page.mouse.move(400, 400)
        page.mouse.move(600, 420)
        page.keyboard.press("Escape")
        check(not page.evaluate("document.body.classList.contains('tool-laser')"), "Esc sale del láser", fails)

        # dibujo
        page.keyboard.press("d")
        page.mouse.move(300, 300)
        page.mouse.down()
        for k in range(10):
            page.mouse.move(300 + k * 30, 300 + k * 10)
        page.mouse.up()
        sid = page.evaluate("document.querySelector('#stage > section.slide.active').dataset.id")
        strokes = page.evaluate(f"(Deck.state.ink['{sid}']||[]).length")
        check(strokes == 1, "D + arrastrar crea un trazo", fails)
        page.keyboard.press("Control+z")
        check(page.evaluate(f"(Deck.state.ink['{sid}']||[]).length") == 0, "Ctrl+Z deshace el trazo", fails)
        page.keyboard.press("Escape")

        # comentario anclado
        page.keyboard.press("Shift+C")
        page.mouse.click(800, 450)
        page.wait_for_selector(".pin-pop textarea")
        page.fill(".pin-pop textarea", "Revisar este dato")
        page.click(".pin-pop [data-x='ok']")
        check(page.evaluate(f"(Deck.state.comments['{sid}']||[]).length") == 1, "Shift+C + clic crea un comentario", fails)
        check(page.locator("#comments .pin").count() == 1, "el pin del comentario se muestra", fails)

        # notas
        page.keyboard.press("t")
        page.wait_for_timeout(300)
        page.fill("#notes-input", "Acuerdo: validar con el equipo")
        check(page.evaluate(f"Deck.state.notes['{sid}']") == "Acuerdo: validar con el equipo", "T abre notas y se guardan", fails)
        check("Acuerdo: validar" in page.evaluate("Deck.minute()"), "la minuta incluye las notas", fails)
        page.keyboard.press("Escape")
        page.evaluate("document.activeElement && document.activeElement.blur()")
        page.keyboard.press("t")

        # edición en vivo
        page.keyboard.press("e")
        check(page.evaluate("document.querySelectorAll('[contenteditable]').length > 0"), "E activa la edición", fails)
        page.keyboard.press("Escape")
        page.keyboard.press("e")

        # vista general y paleta
        page.keyboard.press("o")
        check(page.locator("#overview .thumb").count() == n, "O muestra la vista general", fails)
        page.keyboard.press("Escape")
        page.keyboard.press("g")
        page.wait_for_function("document.activeElement && document.activeElement.id === 'palette-input'")
        page.keyboard.type("presentador")
        check(page.locator("#palette li").count() >= 1, "G abre la búsqueda", fails)
        page.keyboard.press("Escape")

        # quiz
        page.evaluate("Deck.goto(9)")
        page.wait_for_timeout(200)
        page.keyboard.press("2")
        check(page.locator(".slide.active .quiz-opt.correct").count() == 1, "tecla 2 responde el quiz", fails)

        # guardar como HTML
        with page.expect_download() as dl:
            page.keyboard.press("Control+s")
        path = dl.value.path()
        saved = Path(path).read_text(encoding="utf-8") if path else ""
        check("Revisar este dato" in saved, "Ctrl+S descarga HTML con comentarios incluidos", fails)

        # vista del presentador
        with page.expect_popup() as pop:
            page.keyboard.press("s")
        pw = pop.value
        pw.wait_for_function("window.Deck && document.body.classList.contains('presenter')")
        pw.wait_for_timeout(400)
        pw.keyboard.press("ArrowRight")
        page.wait_for_timeout(900)
        check(page.evaluate("Deck.index") == 10, "el presentador mueve la ventana de audiencia", fails)

        check(not errors, "sin errores de JavaScript" + (f": {errors[:2]}" if errors else ""), fails)
        browser.close()
    return fails


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--browsers", default="chromium,firefox,webkit")
    a = ap.parse_args()
    subprocess.run([sys.executable, str(SKILL / "scripts" / "build_deck.py"), str(DECK_JSON)], check=True)
    fails: list[str] = []
    for b in a.browsers.split(","):
        fails += [f"{b}: {f}" for f in run(b.strip())]
    print("RESULTADO:", "OK" if not fails else f"{len(fails)} fallo(s)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
