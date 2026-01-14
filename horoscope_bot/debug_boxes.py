
from PIL import Image, ImageDraw
import os

TEMPLATE_DIR = "d:/zodiac sign pdf/final-template-without-para-date"
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "zodiac_sign_template_page-0001.jpg")

# Constants in image_generator.py
PARA1_X = 242
PARA1_Y = 247
PARA1_W = 1022 - 242
PARA1_H = 548 - 247

PARA2_X = 54
PARA2_Y = 712
PARA2_W = 843 - 54
PARA2_H = 1008 - 712

DATE_CENTER_X = 542
DATE_CENTER_Y = 83

def generate_debug_image():
    try:
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        if img.size != (1080, 1080):
            img = img.resize((1080, 1080))
            
        draw = ImageDraw.Draw(img)
        
        # Draw Red Box for Top Para
        draw.rectangle(
            [PARA1_X, PARA1_Y, PARA1_X + PARA1_W, PARA1_Y + PARA1_H], 
            outline="red", width=5
        )
        
        # Draw Blue Box for Bottom Para
        draw.rectangle(
            [PARA2_X, PARA2_Y, PARA2_X + PARA2_W, PARA2_Y + PARA2_H], 
            outline="blue", width=5
        )
        
        # Draw Green Box for Date Center
        r = 10
        draw.ellipse(
            [DATE_CENTER_X - r, DATE_CENTER_Y - r, DATE_CENTER_X + r, DATE_CENTER_Y + r],
            outline="green", width=5
        )
        
        img.save("debug_alignment_boxes.jpg")
        print("Debug image 'debug_alignment_boxes.jpg' created.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_debug_image()
