#!/usr/bin/env python3
"""
doctor.py — Verifica que el entorno puede generar presentaciones con calidad.

Uso:  python scripts/doctor.py
Revisa Python, paquetes obligatorios, extractores opcionales y que Chromium arranque.
Indica el comando exacto para instalar lo que falte según el sistema operativo.
"""
from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REQ = SKILL_DIR / "requirements.txt"


def py_cmd() -> str:
    return "py" if platform.system() == "Windows" else "python3"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ok = True
    py = py_cmd()
    print(f"Sistema: {platform.system()} {platform.release()} · Python {platform.python_version()}")
    print(f"Skill:   {SKILL_DIR}")
    if sys.version_info < (3, 10):
        ok = False
        print("✗ Se requiere Python 3.10 o superior")
    else:
        print("✓ Python ≥ 3.10")

    required = {"playwright": "QA visual y PDF (obligatorio)", "PIL": "optimizar imágenes (obligatorio)"}
    optional = {"pypdf": "leer PDF", "docx": "leer Word (python-docx)", "pptx": "leer PowerPoint (python-pptx)", "openpyxl": "leer Excel"}
    for mod, why in required.items():
        try:
            importlib.import_module(mod)
            print(f"✓ {mod:<10} {why}")
        except ImportError:
            ok = False
            print(f"✗ {mod:<10} {why}")
    for mod, why in optional.items():
        try:
            importlib.import_module(mod)
            print(f"✓ {mod:<10} {why}")
        except ImportError:
            print(f"· {mod:<10} {why} (solo si usas esa fuente)")

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            b.close()
        print("✓ Chromium arranca correctamente")
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"✗ Chromium no disponible: {str(e).splitlines()[0][:120]}")

    for f in ["assets/engine/engine.js", "assets/engine/engine.css", "assets/engine/template.html", "assets/icons.json"]:
        if not (SKILL_DIR / f).exists():
            ok = False
            print(f"✗ Falta {f} (copia la carpeta completa de la skill)")

    if not ok:
        print("\nPara instalar lo necesario:")
        print(f'  {py} -m pip install -r "{REQ}"')
        print(f"  {py} -m playwright install chromium")
        if platform.system() == "Linux":
            print(f"  (Linux sin librerías gráficas: {py} -m playwright install --with-deps chromium)")
        return 1
    print("\nTodo listo para generar presentaciones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
