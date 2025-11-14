import os
import random

from core.context import Context


def get_banner(context: Context):
    """Dynamically import the text art banner"""
    text_arts: list[str] = os.listdir(context.TEXT_ART_DIR)
    if not text_arts:
        return None
    index = random.randint(0, len(text_arts) - 1)
    text_art = None
    with open(context.TEXT_ART_DIR / text_arts[index], "r", encoding="utf8") as file:
        text_art = file.read()
    return text_art


def image_to_pixel_art(image_path: str, width: int = 50):
    # from PIL import Image
    # img = Image.open(image_path).convert("RGB")
    # img = img.resize((width, int(img.height * width / img.width * 0.5)))

    # for y in range(img.height):
    #     for x in range(img.width):
    #         r, g, b = img.getpixel((x, y))
    #         print(f"\033[48;2;{r};{g};{b}m ", end="")
    #     print("\033[0m")  # Reset at the end of the line
    pass
