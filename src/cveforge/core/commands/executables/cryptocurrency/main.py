import typer
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context

from bip_utils.bip.bip39.bip39_seed_generator import Bip39SeedGenerator
from bip_utils.bip.bip44.bip44 import Bip44
from bip_utils.bip.bip44_base.bip44_base import Bip44Changes
from bip_utils.bip.conf.bip44.bip44_coins import Bip44Coins

from eth_account import Account


def derive_privkey_from_mnemonic(mnemonic: str, derivation_path_index: int = 0):
    """
    Derive private key and address for derivation path m/44'/60'/0'/0/<index>.
    Returns (privkey_hex_prefixed, address_checksum).
    """
    # generate seed from mnemonic (no passphrase)
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # create BIP44 master for Ethereum
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

    # derive account: m/44'/60'/0'/0/index
    acct = (
        bip44_mst.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(derivation_path_index)
    )

    # get raw private key hex (no 0x)
    priv_hex = acct.PrivateKey().Raw().ToHex()

    # get address using eth-account for correct checksum formatting
    acct_obj = Account.from_key(bytes.fromhex(priv_hex))
    return "0x" + priv_hex, acct_obj.address


@tcve_command()
def crypto(
    context: Context,
    network_name: str = typer.Argument(default="eth"),
    index: int = typer.Option(default=0),
    mnemonic_to_private_key: bool = typer.Option(default=False),
):
    if network_name == "eth":
        if mnemonic_to_private_key:
            mnemonic: str = context.console_session.prompt(
                "Recovery phrase: ", is_password=True
            )
            priv_hex, address = derive_privkey_from_mnemonic(mnemonic, index)
            context.stdout.print("Private Key: ", priv_hex)
            context.stdout.print("Public Address: ", address)
    else:
        raise NotImplementedError("Not implemented yet")
