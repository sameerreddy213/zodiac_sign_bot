
import os
import time
from scraper import fetch_horoscope
from image_generator import generate_horoscope_images
from PIL import Image

from image_generator import generate_horoscope_images, fit_text_to_box, get_font
import image_generator
from PIL import Image, ImageDraw

def verify_with_real_data():
    # Helper to mock template loading
    def mock_open(path):
        return Image.new("RGB", (1080, 1080), (0, 0, 0))
    
    # Patch the Image object IMPORTED inside image_generator
    image_generator.Image.open = mock_open
    
    print("Fetching Aries horoscope...")
    # Fetch Aries for verification
    result = fetch_horoscope("aries")
    if isinstance(result, tuple):
        text = result[0]
    else:
        text = result
        
    if not text or len(text) < 10:
        text = "Sample text " * 50
        print("Scraping failed or empty, using fallback text.")
    else:
        print(f"Fetched {len(text)} chars.")

    # Create dummy list for generator
    horoscopes = [{"sign": "aries", "text": text}, {"sign": "taurus", "text": text}]
    
    print("Generating image...")
    paths = generate_horoscope_images(horoscopes, "Test Date")
    print(f"Generated: {paths}")
    
    # Analyze alignment
    img_path = paths[0]
    img = Image.open(img_path).convert("L")
    
    def get_first_pixel_x(y_start, y_end):
        width, height = img.size
        min_x = width
        for y in range(y_start, y_end, 5):
            for x in range(0, width):
                if img.getpixel((x, y)) > 100: # Light text
                    if x < min_x: min_x = x
                    break
        return min_x

    # Top Para Region
    p1_x = get_first_pixel_x(247, 548)
    print(f"Top Para Start X: {p1_x}")
    
    # Bottom Para Region
    p2_x = get_first_pixel_x(712, 1008)
    print(f"Bottom Para Start X: {p2_x}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("conf.env")
    verify_with_real_data()
