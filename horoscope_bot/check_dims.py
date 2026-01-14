from PIL import Image
import os

paths = [
    "d:/GITHUB REPOS/zodiac_sign_bot/Template-2/1.jpg",
    "d:/GITHUB REPOS/zodiac_sign_bot/you_created.jpg"
]

for p in paths:
    if os.path.exists(p):
        img = Image.open(p)
        print(f"{p}: {img.size}")
    else:
        print(f"{p}: Not found")
