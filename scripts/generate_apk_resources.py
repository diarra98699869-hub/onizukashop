"""
Génère les ressources graphiques officielles pour `@capacitor/assets` (APK Android & IPA iOS) :
- resources/icon.png (1024x1024)
- resources/icon-foreground.png (1024x1024 Adaptive Icon Android)
- resources/icon-background.png (1024x1024 Fond Obsidian #0d0e12)
- resources/splash.png (2732x2732 SplashScreen centré Obsidian & Gold)
- resources/splash-dark.png (2732x2732)
"""
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent.parent
RES_DIR = BASE_DIR / 'resources'
RES_DIR.mkdir(parents=True, exist_ok=True)

LOGO_SRC = BASE_DIR / 'static' / 'images' / 'logo_icon.png'
OBSIDIAN = (13, 14, 18, 255)
GOLD = (250, 204, 21, 255)

logo = Image.open(LOGO_SRC).convert('RGBA')

# 1. Background 1024x1024
bg_1024 = Image.new('RGBA', (1024, 1024), OBSIDIAN)
bg_1024.save(RES_DIR / 'icon-background.png', 'PNG')

# 2. Foreground 1024x1024 (zone de sécurité Adaptive Icon Android = 66%)
fg_1024 = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
logo_fg = logo.copy()
logo_fg.thumbnail((640, 640), Image.Resampling.LANCZOS)
fg_1024.paste(logo_fg, ((1024 - logo_fg.width) // 2, (1024 - logo_fg.height) // 2), logo_fg)
fg_1024.save(RES_DIR / 'icon-foreground.png', 'PNG')

# 3. Icone principale 1024x1024
icon_1024 = bg_1024.copy()
draw_ic = ImageDraw.Draw(icon_1024)
draw_ic.rounded_rectangle([48, 48, 976, 976], radius=210, outline=GOLD, width=10)
icon_1024.paste(logo_fg, ((1024 - logo_fg.width) // 2, (1024 - logo_fg.height) // 2), logo_fg)
icon_1024.save(RES_DIR / 'icon.png', 'PNG')

# 4. Splash Screen 2732x2732 (Android & iOS universel)
splash = Image.new('RGBA', (2732, 2732), OBSIDIAN)
logo_sp = logo.copy()
logo_sp.thumbnail((680, 680), Image.Resampling.LANCZOS)
splash.paste(logo_sp, ((2732 - logo_sp.width) // 2, (2732 - logo_sp.height) // 2), logo_sp)
splash.save(RES_DIR / 'splash.png', 'PNG')
splash.save(RES_DIR / 'splash-dark.png', 'PNG')

print("Ressources natives APK/iOS générées dans resources/ :", [p.name for p in RES_DIR.glob('*.png')])
