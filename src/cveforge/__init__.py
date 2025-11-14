"""
Strongly inspired by Metasploit but with a different target in mind, used to overcome difficulties
with existent tools and cheap connections like those given by the country where I reside.
"""
from cveforge.utils.args import ForgeParser as ForgeParser # type: ignore
from cveforge.core.commands.run import tcve_command as tcve_command # type: ignore
from cveforge.core.commands.run import tcve_exploit as tcve_exploit # type: ignore
from cveforge.core.context import Context as Context # type: ignore
