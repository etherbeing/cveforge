from core.io import OUT
from utils.graphic import get_banner


def banner():
    OUT.print(get_banner(), new_line_start=True, justify="center", no_wrap=True, width=OUT.width)
    