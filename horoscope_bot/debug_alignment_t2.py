from PIL import Image, ImageDraw
import os

# Config from image_generator.py (Template 2)
CONFIG = {
    "date_coords": (353, 43, 671, 99),
    "para1_coords": (74, 313, 481, 959),
    "para2_coords": (560, 314, 965, 960),
}

TEMPLATE_PATH = "d:/GITHUB REPOS/zodiac_sign_bot/Template-2/1.jpg"

def draw_boxes():
    try:
        img = Image.open(TEMPLATE_PATH).convert("RGB")
    except Exception as e:
        print(f"Error opening {TEMPLATE_PATH}: {e}")
        return

    draw = ImageDraw.Draw(img)

    # Helper to draw rect
    def draw_rect(coords, color, label):
        x1, y1, x2, y2 = coords
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)
        draw.text((x1, y1-20), label, fill=color)

    draw_rect(CONFIG["date_coords"], "red", "DATE")
    draw_rect(CONFIG["para1_coords"], "blue", "PARA1")
    draw_rect(CONFIG["para2_coords"], "green", "PARA2")
    
    # Also draw centers
    dx1, dy1, dx2, dy2 = CONFIG["date_coords"]
    cx, cy = (dx1+dx2)//2, (dy1+dy2)//2
    draw.line([(cx-10, cy), (cx+10, cy)], fill="red", width=3)
    draw.line([(cx, cy-10), (cx, cy+10)], fill="red", width=3)

    img.save("debug_template_2_boxes.jpg")
    print("Saved debug_template_2_boxes.jpg")

if __name__ == "__main__":
    draw_boxes()
