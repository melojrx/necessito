#!/usr/bin/env python3
"""Gera ícones PWA a partir de static/img/logo2.png
Cria variantes normais e maskable + apple-touch-icon.
"""
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / 'static' / 'img'
SRC = IMG_DIR / 'logo2.png'
ICONS_DIR = IMG_DIR / 'icons'
SIZES = [192, 256, 384, 512]
PADDING_RATIO = 0.18  # para maskable


def generate():
    if not SRC.exists():
        raise SystemExit(f'Arquivo base não encontrado: {SRC}')
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    base = Image.open(SRC).convert('RGBA')

    for size in SIZES:
        # normal
        normal = base.resize((size, size), Image.LANCZOS)
        normal_path = ICONS_DIR / f'icon-{size}x{size}.png'
        normal.save(normal_path, format='PNG')
        print('[OK]', normal_path.relative_to(BASE_DIR))

        # maskable (padding)
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        inner = int(size * (1 - 2 * PADDING_RATIO))
        inner_img = base.resize((inner, inner), Image.LANCZOS)
        offset = int(size * PADDING_RATIO)
        canvas.paste(inner_img, (offset, offset), inner_img)
        mask_path = ICONS_DIR / f'icon-{size}x{size}-maskable.png'
        canvas.save(mask_path, format='PNG')
        print('[OK]', mask_path.relative_to(BASE_DIR))

    # apple-touch-icon 180x180
    apple = base.resize((180, 180), Image.LANCZOS)
    apple_path = IMG_DIR / 'apple-touch-icon.png'
    apple.save(apple_path, format='PNG')
    print('[OK]', apple_path.relative_to(BASE_DIR))

    print('\nConcluído.')


if __name__ == '__main__':
    generate()
