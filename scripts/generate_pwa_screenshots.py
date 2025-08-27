#!/usr/bin/env python3
"""
Script para gerar screenshots placeholder válidos para PWA
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_screenshot(width, height, filename, title, subtitle=""):
    """Cria um screenshot placeholder com dimensões específicas"""
    
    # Criar imagem com fundo gradiente
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    # Gradiente simples (azul para branco)
    for y in range(height):
        ratio = y / height
        r = int(255 * ratio + 13 * (1 - ratio))
        g = int(255 * ratio + 110 * (1 - ratio))
        b = int(255 * ratio + 253 * (1 - ratio))
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
    
    # Tentar usar fonte do sistema, fallback para fonte padrão
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                                      size=min(48, width//20))
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                                         size=min(24, width//40))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Calcular posição do texto
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    # Desenhar título
    title_x = (width - title_width) // 2
    title_y = height // 2 - title_height - 20
    draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
    
    # Desenhar subtítulo se fornecido
    if subtitle:
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + title_height + 10
        draw.text((subtitle_x, subtitle_y), subtitle, fill='#f0f0f0', font=subtitle_font)
    
    # Desenhar logo placeholder (círculo)
    logo_size = min(80, width//16)
    logo_x = (width - logo_size) // 2
    logo_y = height // 2 + 40
    draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                fill='#ffffff', outline='#0d6efd', width=3)
    
    # Salvar imagem
    img.save(filename, 'PNG', optimize=True)
    print(f"Screenshot criado: {filename} ({width}x{height})")

def main():
    # Diretório de screenshots
    screenshot_dir = "/home/jrmelo/projetos/necessito/static/img/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Gerar screenshots
    create_screenshot(
        1280, 720, 
        os.path.join(screenshot_dir, "desktop-1.png"),
        "Indicai Marketplace",
        "Conectando necessidades com soluções"
    )
    
    create_screenshot(
        375, 812,
        os.path.join(screenshot_dir, "mobile-1.png"), 
        "Indicai",
        "Marketplace mobile"
    )
    
    print("Screenshots PWA gerados com sucesso!")

if __name__ == "__main__":
    main()
