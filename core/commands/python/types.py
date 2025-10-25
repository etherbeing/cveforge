
from typing import TypedDict


class Package(TypedDict):
    remote_url: str
    wheel_url: str

type VersionedPackage = dict[str, Package]
