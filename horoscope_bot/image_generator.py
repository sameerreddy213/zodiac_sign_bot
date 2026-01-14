
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

# Template Configurations
TEMPLATE_CONFIGS = {
    "1": {
        "dir_name": "final-template-without-para-date",
        "file_pattern": "zodiac_sign_template_page-{:04d}.jpg",
        "date_coords": (221, 48, 863, 122), # (x1, y1, x2, y2)
        "para1_coords": (242, 247, 1022, 548),
        "para2_coords": (54, 712, 843, 1008),
        "text_color": (230, 221, 212), # Off-white
        "date_color": (28, 56, 33),   # Dark Green
        "date_format": "full",        # Include year
        "font_name_text": "text",
        "font_name_date": "date"
    },
    "2": {
        "dir_name": "Template-2",
        "file_pattern": "{}.jpg",     # 1.jpg, 2.jpg...
        "date_coords": (383, 43, 701, 99),    # Moved Left -10 (Half of last +20 shift)
        "para1_coords": (94, 333, 501, 979),  
        "para2_coords": (600, 334, 1015, 980), 
        "text_color": (0, 0, 0),      # Black
        # Ensure pure white
        "date_color": (255, 255, 255),
        "date_format": "no_year",     # Exclude year
        "font_name_text": "text",
        "font_name_date": "date" 
    }
}

def generate_horoscope_images(horoscopes, date_label, template_id="1", assets_dir=ASSETS_DIR):
    image_paths = []
    
    config = TEMPLATE_CONFIGS.get(template_id, TEMPLATE_CONFIGS["1"])
    template_dir = os.path.join(assets_dir, config["dir_name"])
    
    # Pre-calculate dimensions from coords
    # Date
    dx1, dy1, dx2, dy2 = config["date_coords"]
    date_center_x = (dx1 + dx2) // 2
    date_center_y = (dy1 + dy2) // 2
    
    
    # Para 1
    p1x1, p1y1, p1x2, p1y2 = config["para1_coords"]
    p1_w = p1x2 - p1x1
    p1_h = p1y2 - p1y1
    
    # Para 2
    p2x1, p2y1, p2x2, p2y2 = config["para2_coords"]
    p2_w = p2x2 - p2x1
    p2_h = p2y2 - p2y1
    
    # Format Date Label if needed
    display_date = date_label
    if config["date_format"] == "no_year":
        # Assumes date_label is like "14 January 2026"
        parts = date_label.split()
        if len(parts) >= 2:
            display_date = f"{parts[0]} {parts[1]}"
    
    for i in range(0, 12, 2):
        if i >= len(horoscopes): break
        
        template_idx = (i // 2) + 1
        template_filename = config["file_pattern"].format(template_idx)
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
        # Ensure bold for date if requested or default
        date_font = get_font(config["font_name_date"], 47)
        draw.text((date_center_x, date_center_y), display_date, font=date_font, fill=config["date_color"], anchor="mm", align="center")
        
        # 2. Top Sign
        sign1 = horoscopes[i]
        draw_text_block(draw, sign1['text'], p1x1, p1y1, p1_w, p1_h, color=config["text_color"])
        
        # 3. Bottom Sign
        if i+1 < len(horoscopes):
            sign2 = horoscopes[i+1]
            draw_text_block(draw, sign2['text'], p2x1, p2y1, p2_w, p2_h, color=config["text_color"])
            
        filename = f"horoscope_{template_idx}.jpg"
        img.save(filename, quality=95)
        image_paths.append(filename)
        
    return image_paths



def draw_text_block(draw, text, x, y, w, h, color=TEXT_COLOR):
    font, lines, line_height = fit_text_to_box(
        draw, text, w, h, 
        start_font_size=24, min_font_size=16, font_name='text'
    )
    
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=color)
        current_y += line_height

if __name__ == "__main__":
    # Test
    sample_data = [{"sign": str(i), "text": "Sample horoscope text " * 10} for i in range(12)]
    generate_horoscope_images(sample_data, "14 January 2026")
    print("Templates generated.")
