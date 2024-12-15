import os
import random
from core.context import Context


def get_banner():
    """Dynamically import the text art banner"""
    text_arts = os.listdir(Context.TEXT_ART_DIR)
    if not text_arts:
        return None
    index = random.randint(0, len(text_arts) - 1)
    text_art = None
    with open(Context.TEXT_ART_DIR / text_arts[index], "r", encoding="utf8") as file:
        text_art = file.read()
    return text_art
