#!/usr/bin/env python3
"""Gera ícones PWA consistentes a partir de um SVG base.
Requisitos: cairosvg, Pillow
Uso:
  python scripts/generate_pwa_icons.py
Saída:
  static/img/icons/icon-<size>x<size>.png
  static/img/icons/icon-<size>x<size>-maskable.png (com padding extra)
"""
from pathlib import Path
import io
import cairosvg
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / 'static' / 'img' / 'icons'
BASE_SVG = ICONS_DIR / 'base-icon.svg'
SIZES = [192, 256, 384, 512]
MASKABLE_PADDING_RATIO = 0.18  # 18% padding


def ensure_dirs():
    ICONS_DIR.mkdir(parents=True, exist_ok=True)


def svg_to_png_bytes(svg_path: Path, size: int) -> bytes:
    return cairosvg.svg2png(url=str(svg_path), output_width=size, output_height=size)


def write_png(data: bytes, dest: Path):
    dest.write_bytes(data)
    print(f"[OK] {dest.relative_to(BASE_DIR)}")


def make_maskable(png_bytes: bytes, size: int) -> bytes:
    img = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
    new_size = size
    padding = int(size * MASKABLE_PADDING_RATIO)
    canvas_size = new_size
    canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    inner_box = (padding, padding, canvas_size - padding, canvas_size - padding)
    # Redimensiona a arte original para caber na área interna mantendo aspecto
    inner_w = inner_box[2] - inner_box[0]
    inner_h = inner_box[3] - inner_box[1]
    img_resized = img.resize((inner_w, inner_h), Image.LANCZOS)
    canvas.paste(img_resized, (inner_box[0], inner_box[1]), img_resized)
    out = io.BytesIO()
    canvas.save(out, format='PNG')
    return out.getvalue()


def main():
    if not BASE_SVG.exists():
        raise SystemExit(f"Base SVG não encontrado: {BASE_SVG}")
    ensure_dirs()

    for size in SIZES:
        raw_png = svg_to_png_bytes(BASE_SVG, size)
        write_png(raw_png, ICONS_DIR / f"icon-{size}x{size}.png")
        maskable_png = make_maskable(raw_png, size)
        write_png(maskable_png, ICONS_DIR / f"icon-{size}x{size}-maskable.png")

    # Apple touch icon (180x180) baseado em 192 -> recorte central
    apple_size = 180
    base_png = Image.open(io.BytesIO(svg_to_png_bytes(BASE_SVG, 192))).convert('RGBA')
    apple_img = base_png.resize((apple_size, apple_size), Image.LANCZOS)
    apple_path = BASE_DIR / 'static' / 'img' / 'apple-touch-icon.png'
    apple_img.save(apple_path, format='PNG')
    print(f"[OK] {apple_path.relative_to(BASE_DIR)}")

    print('\nConcluído. Atualize o service worker versão se quiser forçar update.')


if __name__ == '__main__':
    main()
