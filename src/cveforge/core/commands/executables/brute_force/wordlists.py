from typing import Optional
import typer
import wordlist
from cveforge.core.commands.run import tcve_command


@tcve_command(name="wordlist")
def wordlist_command(
    minimum: int = typer.Option(default=1, help="Minimum length of the words"),
    maximum: int = typer.Option(default=10, help="Maximum length of the words"),
    charset: str = typer.Option(
        default="lower,upper,digits",
        help="Character sets to use: lower, upper, digits, special",
    ),
    output: Optional[str] = typer.Option(
        default=None, help="Output file to save the generated wordlist"
    ),
    interactive: bool = typer.Option(
        default=False, help="Generate words interactively"
    ),
    pattern: Optional[str] = typer.Option(default=None),
    noop: bool = typer.Option(
        default=False,
        help="Show the number of combinations without generating the wordlist",
    ),
):
    """
    Brute Force Wordlist Command
    usage:
        wordlist generate --min 1 --max 10 --charset lower,upper,digits,special --output /path/to/wordlist.txt # generates a wordlist with the given parameters
        wordlist generate --min 1 --max 10 --charset lower --interactive # generates an random word each time you press enter
        wordlist generate --noop --min 1 --max 10 --charset lower,upper,digits,special # shows how many combinations would be generated without generating the wordlist
        wordlist load --file /path/to/wordlist.txt
    """
    sanitized_charset = charset.split(",")
    assert all(
        c in ["lower", "upper", "digits", "special"] for c in sanitized_charset
    ), "Invalid charset specified"
    charmap = ""
    if "lower" in sanitized_charset:
        charmap += "abcdefghijklmnopqrstuvwxyz"
    if "upper" in sanitized_charset:
        charmap += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if "digits" in sanitized_charset:
        charmap += "0123456789"
    if "special" in sanitized_charset:
        charmap += "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"

    total_combinations = sum(len(charmap) ** i for i in range(minimum, maximum + 1))
    if noop:
        typer.echo(f"Total combinations: {total_combinations}")
        return
    generated = wordlist.Generator(charset=charset)
    if pattern:
        generator = generated.generate_with_pattern(pattern=pattern)
    else:
        generator = generated.generate(minimum, maximum)
    for word in generator:
        typer.echo(word)
