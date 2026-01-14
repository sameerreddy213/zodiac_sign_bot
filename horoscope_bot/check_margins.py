
from PIL import Image

def check_margins():
    img_path = "d:/zodiac sign pdf/horoscope_bot/horoscope_1.jpg"
    img = Image.open(img_path).convert("L")
    
    # Threshold: BG is dark (~15), Text is light (230).
    # So text pixels will be > 100.
    
    width, height = img.size
    
    # Y-ranges from previous analysis:
    # Region 1 (Date): Y=59 to 113
    # Region 2 (Para 1): Y=254 to 540
    # Region 3 (Para 2): Y=717 to 996
    
    def get_x_bounds(y_range):
        min_x = width
        max_x = 0
        pixel_count = 0
        
        for y in range(y_range[0], y_range[1], 2): # Scan tighter (every 2nd line)
            for x in range(0, width):
                # Check for light text pixel (threshold > 100)
                if img.getpixel((x, y)) > 100:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    pixel_count += 1
        
        if pixel_count == 0: return (0, 0)
        return min_x, max_x

    # Region 1 (Para 1): Y=254 to 540 (Approx from earlier)
    # Region 2 (Para 2): Y=717 to 996
    
    # Let's widen the scan to match user map Y's just to be safe
    # User said Top: 247 to 548
    # User said Bottom: 712 to 1008
    
    b1 = get_x_bounds((247, 548))
    b2 = get_x_bounds((712, 1008))
    
    print(f"Top Para (Template-1): X_Start={b1[0]}, X_End={b1[1]}, Width={b1[1]-b1[0]}")
    print(f"Bottom Para (Template-1): X_Start={b2[0]}, X_End={b2[1]}, Width={b2[1]-b2[0]}")

if __name__ == "__main__":
    check_margins()
