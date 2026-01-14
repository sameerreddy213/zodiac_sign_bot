from PIL import Image, ImageDraw
import os

# Current Config from image_generator.py
# Adjusted Para 2 X1 from 560 to 550 based on analysis to give more room
CONFIG = {
    "date_coords": (373, 43, 691, 99),
    "para1_coords": (94, 333, 501, 979),
    "para2_coords": (600, 334, 1015, 980),
}

TEMPLATE_PATH = "d:/GITHUB REPOS/zodiac_sign_bot/Template-2/1.jpg"
OUTPUT_PATH = "d:/GITHUB REPOS/zodiac_sign_bot/debug_boxes.jpg"

def draw_boxes():
    try:
        img = Image.open(TEMPLATE_PATH).convert("RGB")
    except Exception as e:
        print(f"Error opening {TEMPLATE_PATH}: {e}")
        return

    draw = ImageDraw.Draw(img)

    def draw_rect(coords, color, label):
        x1, y1, x2, y2 = coords
        # Draw outline
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)
        # Draw semi-transparent fill
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        d_overlay = ImageDraw.Draw(overlay)
        d_overlay.rectangle([x1, y1, x2, y2], fill=(*color, 64))
        img.paste(Image.alpha_composite(img.convert('RGBA'), overlay), (0,0))
        
        draw.text((x1, y1-25), f"{label} {coords}", fill=color)

    # Date (Red)
    draw_rect(CONFIG["date_coords"], (255, 0, 0), "DATE")
    
    # Para 1 (Blue)
    draw_rect(CONFIG["para1_coords"], (0, 0, 255), "PARA 1 (Left)")
    
    # Para 2 (Green)
    draw_rect(CONFIG["para2_coords"], (0, 255, 0), "PARA 2 (Right)")
    
    img.convert("RGB").save(OUTPUT_PATH)
    print(f"Saved visualization to {OUTPUT_PATH}")

if __name__ == "__main__":
    draw_boxes()
