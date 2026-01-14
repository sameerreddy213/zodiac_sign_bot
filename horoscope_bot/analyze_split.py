from PIL import Image

REF_IMG = "d:/GITHUB REPOS/zodiac_sign_bot/my_image.jpg"

def analyze_split(img_path, threshold=100):
    try:
        img = Image.open(img_path).convert("RGB")
        width, height = img.size
        pixels = img.load()
        
        # Black text range
        r_max, g_max, b_max = (threshold, threshold, threshold)
        
        def scan_rect(x_start, x_end, y_start, y_end):
            min_x, max_x = x_end, x_start
            min_y, max_y = y_end, y_start
            found = False
            
            for y in range(y_start, y_end):
                for x in range(x_start, x_end):
                    r, g, b = pixels[x, y]
                    if r <= r_max and g <= g_max and b <= b_max:
                        found = True
                        if x < min_x: min_x = x
                        if x > max_x: max_x = x
                        if y < min_y: min_y = y
                        if y > max_y: max_y = y
            return (min_x, min_y, max_x, max_y) if found else None

        mid = width // 2
        
        # Left Side (Para 1)
        left_box = scan_rect(0, mid, 200, height)
        print(f"Left Box (Para 1): {left_box}")
        
        # Right Side (Para 2)
        right_box = scan_rect(mid, width, 200, height)
        print(f"Right Box (Para 2): {right_box}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_split(REF_IMG)
