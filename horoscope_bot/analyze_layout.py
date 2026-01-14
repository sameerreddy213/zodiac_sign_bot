from PIL import Image, ImageChops
import os

REF_IMG = "d:/GITHUB REPOS/zodiac_sign_bot/my_image.jpg"
GEN_IMG = "d:/GITHUB REPOS/zodiac_sign_bot/you_created.jpg"

def get_bbox_of_color(img_path, target_color_range):
    """
    Finds bounding box of pixels matching a color range.
    target_color_range: ((r_min, g_min, b_min), (r_max, g_max, b_max))
    """
    try:
        img = Image.open(img_path).convert("RGB")
    except Exception as e:
        print(f"Could not open {img_path}: {e}")
        return

    width, height = img.size
    pixels = img.load()
    
    (r1, g1, b1), (r2, g2, b2) = target_color_range
    
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found = False

    # Scan the paragraph areas roughly to speed up? No, scan whole image.
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r1 <= r <= r2 and g1 <= g <= g2 and b1 <= b <= b2:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                found = True
                
    if found:
        print(f"[{img_path}] BBox matching color {target_color_range}:")
        print(f"  Rect({min_x}, {min_y}, {max_x}, {max_y})")
        print(f"  Width: {max_x - min_x}, Height: {max_y - min_y}")
        print(f"  Center: ({(min_x+max_x)//2}, {(min_y+max_y)//2})")
    else:
        print(f"[{img_path}] No pixels found in range {target_color_range}")

if __name__ == "__main__":
    print("--- ANALYSIS RESULTS ---")
    
    # Measure Black Text in BODY (Paragraphs) - y > 200
    # Range: (0,0,0) to (100,100,100) - laxer threshold for anti-aliasing
    black_range = ((0, 0, 0), (100, 100, 100))
    
    def analyze_region(img_path, region_name, y_min, y_max, color_range):
        try:
            img = Image.open(img_path).convert("RGB")
            # Crop to region
            crop = img.crop((0, y_min, img.width, y_max))
            
            # Find bounds
            pixels = crop.load()
            (r1, g1, b1), (r2, g2, b2) = color_range
            
            min_x, max_x = crop.width, 0
            min_y, max_y = crop.height, 0
            count = 0
            
            for y in range(crop.height):
                for x in range(crop.width):
                    r, g, b = pixels[x, y]
                    if r1 <= r <= r2 and g1 <= g <= g2 and b1 <= b <= b2:
                        if x < min_x: min_x = x
                        if x > max_x: max_x = x
                        if y < min_y: min_y = y
                        if y > max_y: max_y = y
                        count += 1
            
            if count > 0:
                # Convert back to global coords
                global_min_y = min_y + y_min
                global_max_y = max_y + y_min
                print(f"[{img_path}] {region_name}:")
                print(f"  Rect({min_x}, {global_min_y}, {max_x}, {global_max_y})")
                print(f"  Center X: {(min_x+max_x)//2}")
            else:
                print(f"[{img_path}] {region_name}: No pixels found.")
                
        except Exception as e:
            print(f"Error {img_path}: {e}")

    # Analyze REF
    analyze_region(REF_IMG, "Body (Black Text)", 200, 1080, black_range)
    analyze_region(REF_IMG, "Header (White Text)", 0, 200, ((200, 200, 200), (255, 255, 255)))

    # Analyze GEN
    analyze_region(GEN_IMG, "Body (Black Text)", 200, 1080, black_range)
    analyze_region(GEN_IMG, "Header (White Text)", 0, 200, ((200, 200, 200), (255, 255, 255)))
