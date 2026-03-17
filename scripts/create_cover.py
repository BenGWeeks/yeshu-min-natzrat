"""Create the cover PDF for KDP hardcover (6x9, case laminate).

KDP hardcover (case laminate) cover dimensions:
- Front/back cover: 6.13" x 9.25" (includes 0.125" bleed on 3 sides)
- Spine width: 0.002252" per page (white paper) + 0.08" case laminate addition
- Total width: back + spine + front = 6.13 + spine + 6.13

Design: Dark background (#1a1a2e), gold text (#c9a84c), centered title.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

PROJECT_DIR = Path(__file__).parent.parent
COVER_DIR = PROJECT_DIR / "cover"

# KDP hardcover case laminate dimensions
PAGE_COUNT = 143
DPI = 300

# Cover dimensions (inches)
BLEED = 0.125
FRONT_WIDTH = 6.0 + BLEED  # 6.125" (bleed on outside edge only)
BACK_WIDTH = 6.0 + BLEED
HEIGHT = 9.0 + (2 * BLEED)  # 9.25"
SPINE_WIDTH = (PAGE_COUNT * 0.002252) + 0.08  # white paper + case laminate

# Add 0.125" bleed to outside edges
TOTAL_WIDTH = BACK_WIDTH + BLEED + SPINE_WIDTH + BLEED + FRONT_WIDTH
# back(6.125) + back_inner_bleed(0.125) + spine + front_inner_bleed(0.125) + front(6.125)

print(f"Page count: {PAGE_COUNT}")
print(f"Spine width: {SPINE_WIDTH:.4f}\"")
print(f"Total cover width: {TOTAL_WIDTH:.4f}\"")
print(f"Cover height: {HEIGHT:.4f}\"")

# Pixel dimensions
WIDTH_PX = int(TOTAL_WIDTH * DPI)
HEIGHT_PX = int(HEIGHT * DPI)

print(f"Pixel dimensions: {WIDTH_PX} x {HEIGHT_PX}")

# Colors
BG_COLOR = (26, 26, 46)  # Deep navy/dark
GOLD = (201, 168, 76)  # Gold leaf
SUBTITLE_COLOR = (180, 160, 120)  # Muted gold for subtitle
SPINE_TEXT_COLOR = (201, 168, 76)

# Create image
img = Image.new("RGB", (WIDTH_PX, HEIGHT_PX), BG_COLOR)
draw = ImageDraw.Draw(img)

# Try to find a good serif font
FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
]

FONT_PATHS_REGULAR = [
    "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
]

def find_font(paths, size):
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# Font sizes (in pixels at 300 DPI)
title_font = find_font(FONT_PATHS, int(42 * DPI / 72))  # 42pt
subtitle_font = find_font(FONT_PATHS_REGULAR, int(18 * DPI / 72))  # 18pt
version_font = find_font(FONT_PATHS_REGULAR, int(14 * DPI / 72))  # 14pt
spine_font = find_font(FONT_PATHS, int(14 * DPI / 72))  # 14pt for spine

# Calculate front cover center
front_left = (BACK_WIDTH + BLEED + SPINE_WIDTH + BLEED) * DPI
front_center_x = front_left + (FRONT_WIDTH * DPI) / 2
front_center_y = HEIGHT_PX / 2

# Draw title on front cover — single line
title_text = "Yeshu min Natzrat"

bbox_title = draw.textbbox((0, 0), title_text, font=title_font)
title_w = bbox_title[2] - bbox_title[0]
title_h = bbox_title[3] - bbox_title[1]
title_y = front_center_y - title_h / 2 - int(0.5 * DPI)  # Shift up slightly

draw.text(
    (front_center_x - title_w / 2, title_y),
    title_text, fill=GOLD, font=title_font,
)

# Subtitle below title
subtitle = "A Compiled Canon of the Earliest Teachings"
bbox_sub = draw.textbbox((0, 0), subtitle, font=subtitle_font)
sub_w = bbox_sub[2] - bbox_sub[0]
sub_y = title_y + title_h + int(60 * DPI / 72)
draw.text(
    (front_center_x - sub_w / 2, sub_y),
    subtitle, fill=SUBTITLE_COLOR, font=subtitle_font,
)

# Version at bottom of front cover
version_text = "v1.0"
bbox_ver = draw.textbbox((0, 0), version_text, font=version_font)
ver_w = bbox_ver[2] - bbox_ver[0]
ver_y = HEIGHT_PX - int(1.0 * DPI)  # 1" from bottom
draw.text(
    (front_center_x - ver_w / 2, ver_y),
    version_text, fill=SUBTITLE_COLOR, font=version_font,
)

# Draw spine text (rotated)
spine_center_x = (BACK_WIDTH + BLEED + SPINE_WIDTH / 2) * DPI
spine_text = "Yeshu min Natzrat"

# Create rotated text for spine
spine_bbox = draw.textbbox((0, 0), spine_text, font=spine_font)
spine_text_w = spine_bbox[2] - spine_bbox[0]
spine_text_h = spine_bbox[3] - spine_bbox[1]

# Only add spine text if spine is wide enough
if SPINE_WIDTH * DPI > spine_text_h + 10:
    spine_img = Image.new("RGBA", (spine_text_w + 20, spine_text_h + 20), (0, 0, 0, 0))
    spine_draw = ImageDraw.Draw(spine_img)
    spine_draw.text((10, 10), spine_text, fill=GOLD, font=spine_font)
    spine_rotated = spine_img.rotate(-90, expand=True)

    # Paste rotated spine text
    paste_x = int(spine_center_x - spine_rotated.width / 2)
    paste_y = int(front_center_y - spine_rotated.height / 2)
    img.paste(spine_rotated, (paste_x, paste_y), spine_rotated)

# Add a subtle decorative line on front cover
line_y = int(sub_y - 20 * DPI / 72)
line_half_w = int(1.5 * DPI)  # 1.5" half-width
draw.line(
    [(int(front_center_x - line_half_w), line_y),
     (int(front_center_x + line_half_w), line_y)],
    fill=SUBTITLE_COLOR, width=2,
)

# Save as PNG first, then convert to PDF
COVER_DIR.mkdir(parents=True, exist_ok=True)
png_path = COVER_DIR / "cover.png"
pdf_path = COVER_DIR / "cover.pdf"

img.save(str(png_path), dpi=(DPI, DPI))
print(f"Cover PNG saved to {png_path}")

# Convert to PDF using img2pdf or Pillow
try:
    img.save(str(pdf_path), "PDF", resolution=DPI)
    print(f"Cover PDF saved to {pdf_path}")
except Exception:
    print(f"Could not save PDF directly. PNG available at {png_path}")

print("\nCover created successfully.")
print(f"Upload to KDP as the cover file, or use the PNG for further editing.")
