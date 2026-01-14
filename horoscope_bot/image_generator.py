
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Constants from User Request (Map Coords)
# Date: 863,122,221,48 -> Rect(221, 48, 863, 122)
DATE_CENTER_X = (221 + 863) // 2 # 542
DATE_CENTER_Y = (48 + 122) // 2 # 85

# Top Para: 1022,548,242,247
# Rect(x1=242, y1=247, x2=1022, y2=548)
PARA1_X = 242
PARA1_Y = 247
PARA1_W = 1022 - 242 # 780
PARA1_H = 548 - 247 # 301

# Bottom Para: 54,1008,843,712
# Rect(x1=54, y1=712, x2=843, y2=1008)
PARA2_X = 54
PARA2_Y = 712
PARA2_W = 843 - 54 # 789
PARA2_H = 1008 - 712 # 296

TEXT_COLOR = (230, 221, 212)
DATE_COLOR = (28, 56, 33) # Dark Green from analysis (Fix for visibility)
# Dynamic Path Logic
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Default to parent directory of the script if ASSETS_DIR not set
DEFAULT_ASSETS_DIR = os.path.dirname(BASE_DIR) 
ASSETS_DIR = os.getenv("ASSETS_DIR", DEFAULT_ASSETS_DIR)

TEMPLATE_DIR = os.path.join(ASSETS_DIR, "final-template-without-para-date")
FONT_DIR = ASSETS_DIR

def get_font(name, size):
    font_file = "arial.ttf"
    if name == 'date':
        # Archivo Black
        candidates = ["ArchivoBlack-Regular.ttf", "ArchivoBlack.ttf"]
    else:
        # Glacial Indifference
        candidates = ["GlacialIndifference-Bold.otf", "GlacialIndifference-Bold.ttf"]

    path = font_file
    for cand in candidates:
        full_path = os.path.join(FONT_DIR, cand)
        if os.path.exists(full_path):
            path = full_path
            break
        if os.path.exists(cand):
            path = cand
            break
            
    try:
        font = ImageFont.truetype(path, size)
        return font
    except Exception as e:
        print(f"WARNING: Failed to load font {path}. Error: {e}. Using Default Font.")
        return ImageFont.load_default()

def pixel_text_wrap(draw, text, max_width, font):
    """
    Wraps text based on pixel width rather than character count.
    Returns list of lines.
    """
    words = text.split()
    lines = []
    if not words:
        return []
        
    current_line = []
    
    for word in words:
        # Check width if we add this word
        test_line = ' '.join(current_line + [word])
        w = draw.textlength(test_line, font=font)
        
        if w <= max_width:
            current_line.append(word)
        else:
            # Line is full, push current_line to lines
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word] # Start new line with current word
            else:
                # Word itself is longer than line (unlikely with paragraphs but possible)
                # Force split or just add it? Let's just add it to avoid infinite loops
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines

def fit_text_to_box(draw, text, box_width, box_height, start_font_size=24, min_font_size=14, font_name='text'):
    font_size = start_font_size
    font = None
    lines = []
    
    while font_size >= min_font_size:
        font = get_font(font_name, font_size)
        
        # Use pixel-perfect wrapping
        lines = pixel_text_wrap(draw, text, box_width, font)

        bbox = draw.textbbox((0, 0), "Hg", font=font)
        line_height = bbox[3] - bbox[1] + 12 # Line spacing
        total_height = line_height * len(lines)
        
        if total_height <= box_height:
             # Check explicitly? pixel_text_wrap guarantees strict width compliance
             # unless a single word > width.
             return font, lines, line_height
        
        font_size -= 1
        
    return font, lines, 24

def generate_horoscope_images(horoscopes, date_label, template_dir=TEMPLATE_DIR):
    image_paths = []
    
    for i in range(0, 12, 2):
        if i >= len(horoscopes): break
        
        template_idx = (i // 2) + 1
        template_filename = f"zodiac_sign_template_page-{template_idx:04d}.jpg"
        template_path = os.path.join(template_dir, template_filename)
        
        try:
            img = Image.open(template_path).convert("RGB")
            if img.size != (1080, 1080):
                img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            img = Image.new('RGB', (1080, 1080), color="#0f0f1a")

        draw = ImageDraw.Draw(img)
        
        # 1. Date
        date_font = get_font('date', 47)
        draw.text((DATE_CENTER_X, DATE_CENTER_Y), date_label, font=date_font, fill=DATE_COLOR, anchor="mm", align="center")
        
        # 2. Top Sign
        sign1 = horoscopes[i]
        draw_text_block(draw, sign1['text'], PARA1_X, PARA1_Y, PARA1_W, PARA1_H)
        
        # 3. Bottom Sign
        if i+1 < len(horoscopes):
            sign2 = horoscopes[i+1]
            draw_text_block(draw, sign2['text'], PARA2_X, PARA2_Y, PARA2_W, PARA2_H)
            

        
        filename = f"horoscope_{template_idx}.jpg"
        img.save(filename, quality=95)
        image_paths.append(filename)
        
    return image_paths



def draw_text_block(draw, text, x, y, w, h):
    font, lines, line_height = fit_text_to_box(
        draw, text, w, h, 
        start_font_size=24, min_font_size=16, font_name='text'
    )
    
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=TEXT_COLOR)
        current_y += line_height

if __name__ == "__main__":
    # Test
    sample_data = [{"sign": str(i), "text": "Sample horoscope text " * 10} for i in range(12)]
    generate_horoscope_images(sample_data, "14 January 2026")
    print("Templates generated.")
