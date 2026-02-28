import base64
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
import tempfile

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

TEXT_COLOR_RGB = "230, 221, 212"
DATE_COLOR_RGB = "28, 56, 33"

# Dynamic Path Logic
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Map to root directory assets folder
ROOT_DIR = os.path.dirname(BASE_DIR)
DEFAULT_ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ASSETS_DIR = os.getenv("ASSETS_DIR", DEFAULT_ASSETS_DIR)

TEMPLATE_DIR = os.path.join(ASSETS_DIR, "templates", "final-template-without-para-date")

# Template Configurations
TEMPLATE_CONFIGS = {
    "1": {
        "dir_name": "final-template-without-para-date",
        "file_pattern": "zodiac_sign_template_page-{:04d}.jpg",
        "date_coords": (221, 48, 863, 122), 
        "para1_coords": (242, 247, 1022, 548),
        "para2_coords": (54, 712, 843, 1008),
        "text_color": (230, 221, 212), 
        "date_color": (28, 56, 33),   
        "date_format": "full",        
    },
    "2": {
        "dir_name": "Template-2",
        "file_pattern": "{}.jpg",     
        "date_coords": (383, 43, 701, 99),    
        "para1_coords": (94, 333, 501, 979),  
        "para2_coords": (600, 334, 1015, 980), 
        "text_color": (0, 0, 0),      
        "date_color": (255, 255, 255),
        "date_format": "no_year",     
    }
}

HTML_TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "horoscope.html")

def generate_horoscope_images(horoscopes, date_label, template_id="1", language="english", assets_dir=ASSETS_DIR):
    image_paths = []
    config = TEMPLATE_CONFIGS.get(template_id, TEMPLATE_CONFIGS["1"])
    
    # Language-based Template Directory Routing
    current_dir_name = config["dir_name"]
    current_file_pattern = config["file_pattern"]
    if template_id == "1" and language == "telugu":
        current_dir_name = "template1_telugu"
        current_file_pattern = "{}.png"
        
    template_dir = os.path.join(assets_dir, "templates", current_dir_name)
    
    # Pre-calculate dimensions from coords
    dx1, dy1, dx2, dy2 = config["date_coords"]
    d_rx = dx1
    d_ry = dy1
    d_rw = dx2 - dx1
    d_rh = dy2 - dy1
    
    p1x1, p1y1, p1x2, p1y2 = config["para1_coords"]
    p1_w = p1x2 - p1x1
    p1_h = p1y2 - p1y1
    
    p2x1, p2y1, p2x2, p2y2 = config["para2_coords"]
    p2_w = p2x2 - p2x1
    p2_h = p2y2 - p2y1
    
    # Format Date Label if needed
    display_date = date_label
    if config["date_format"] == "no_year":
        parts = date_label.split()
        if len(parts) >= 2:
            display_date = f"{parts[0]} {parts[1]}"
            
    # Read HTML Template
    with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_template = f.read()
        
    dr, dg, db = config["date_color"]
    tr, tg, tb = config["text_color"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Set viewport explicitly to 1080x1080 to match our template bounds
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        
        if language == "telugu":
            custom_font_path = os.path.join(assets_dir, "fonts", "Potti Sreeramulu Regular.otf").replace("\\", "/")
            font_face_css = f'''
                @font-face {{
                    font-family: 'Potti Sreeramulu';
                    src: url('file:///{custom_font_path}');
                }}
            '''
            font_family = "'Potti Sreeramulu', 'Nirmala UI', sans-serif"
        else:
            font_face_css = ""
            font_family = "'Nirmala UI', 'Gautami', 'Noto Sans Telugu', sans-serif"
            
        for i in range(0, 12, 2):
            if i >= len(horoscopes): break
            
            template_idx = (i // 2) + 1
            template_filename = current_file_pattern.format(template_idx)
            template_path = os.path.join(template_dir, template_filename).replace("\\", "/") # Playwright needs forward slashes
            
            text1 = horoscopes[i]['text']
            # Text formatting
            if language == "telugu":
                text1 = text1.replace("\n", "<br/>")
            
            text2 = ""
            if i+1 < len(horoscopes):
                text2 = horoscopes[i+1]['text']
                if language == "telugu":
                    text2 = text2.replace("\n", "<br/>")
                
            # Inject Background Template correctly with base64 to bypass 'about:blank' local rendering policies
            with open(template_path, "rb") as bf:
                b64_img = base64.b64encode(bf.read()).decode('utf-8')
            b64_uri = f"data:image/jpeg;base64,{b64_img}"
            
            # Render HTML
            rendered_html = html_template \
                .replace("file:///__TEMPLATE_PATH__", b64_uri) \
                .replace("__DISPLAY_DATE__", display_date) \
                .replace("__TEXT1__", text1) \
                .replace("__TEXT2__", text2) \
                .replace("__DATE_RX__", str(d_rx)) \
                .replace("__DATE_RY__", str(d_ry)) \
                .replace("__DATE_RW__", str(d_rw)) \
                .replace("__DATE_RH__", str(d_rh)) \
                .replace("__P1_RX__", str(p1x1)) \
                .replace("__P1_RY__", str(p1y1)) \
                .replace("__P1_RW__", str(p1_w)) \
                .replace("__P1_RH__", str(p1_h)) \
                .replace("__P2_RX__", str(p2x1)) \
                .replace("__P2_RY__", str(p2y1)) \
                .replace("__P2_RW__", str(p2_w)) \
                .replace("__P2_RH__", str(p2_h)) \
                .replace("__DATE_R__", str(dr)) \
                .replace("__DATE_G__", str(dg)) \
                .replace("__DATE_B__", str(db)) \
                .replace("__TEXT_R__", str(tr)) \
                .replace("__TEXT_G__", str(tg)) \
                .replace("__TEXT_B__", str(tb)) \
                .replace("__FONT_FACE_CSS__", font_face_css) \
                .replace("__FONT_FAMILY__", font_family)
            
            page.set_content(rendered_html)
            
            # Explicitly force a tiny delay so the custom TTF/OTF font file parses from disk
            page.wait_for_timeout(250)
                
            out_filename = f"horoscope_{template_idx}.jpg"
            page.screenshot(path=out_filename, type="jpeg", quality=95, full_page=True)
            image_paths.append(out_filename)
            
        browser.close()
        
    return image_paths

if __name__ == "__main__":
    # Test
    sample_data = [{"sign": str(i), "text": "Sample horoscope text " * 10} for i in range(12)]
    generate_horoscope_images(sample_data, "14 January 2026")
    print("Templates generated.")
