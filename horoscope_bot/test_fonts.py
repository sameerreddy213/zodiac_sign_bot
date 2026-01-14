
from PIL import ImageFont
import os

FONT_DIR = "d:/zodiac sign pdf"

def test_fonts():
    candidates = [
        "ArchivoBlack-Regular.ttf", 
        "ArchivoBlack.ttf",
        "GlacialIndifference-Regular.otf", 
        "GlacialIndifference-Regular.ttf"
    ]
    
    print(f"Checking fonts in {FONT_DIR}...")
    
    for cand in candidates:
        full_path = os.path.join(FONT_DIR, cand)
        if os.path.exists(full_path):
            print(f"Found: {cand}")
            try:
                font = ImageFont.truetype(full_path, 24)
                print(f"  [SUCCESS] Loaded {cand}")
                # Check actual name
                try:
                    name = font.getname()
                    print(f"  [INFO] Font Name: {name}")
                except:
                    pass
            except Exception as e:
                print(f"  [FAILURE] Could not load {cand}: {e}")
        else:
             pass # print(f"Missing: {cand}")

if __name__ == "__main__":
    test_fonts()
