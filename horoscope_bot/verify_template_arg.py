from image_generator import generate_horoscope_images
import os

TEMPLATES_DIR = "d:/zodiac sign pdf/final-template-without-para-date"

print("Testing image generation with explicit template_dir...")
try:
    # Dummy data
    sample_data = [{"sign": str(i), "text": "Sample horoscope text " * 10} for i in range(12)]
    
    paths = generate_horoscope_images(sample_data, "Test Date", template_dir=TEMPLATES_DIR)
    
    if len(paths) > 0 and os.path.exists(paths[0]):
        print(f"Success! Generated {len(paths)} images.")
        # Clean up
        for p in paths:
            os.remove(p)
    else:
        print("Failed to generate images.")
except Exception as e:
    print(f"Error during test: {e}")
