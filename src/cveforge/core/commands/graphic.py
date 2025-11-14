from core.commands.run import tcve_command
from core.context import Context
from utils.graphic import get_banner


@tcve_command("banner")
def banner(context: Context):
    context.stdout.print(
        get_banner(context),
        new_line_start=True,
        justify="center",
        no_wrap=True,
        width=context.stdout.width,
    )
