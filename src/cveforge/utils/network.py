from typing import Optional, TypedDict

import psutil


class TIFace(TypedDict):
    is_up: Optional[bool]
    details: list[dict[str, Optional[str]]]


def get_ifaces() -> dict[str, TIFace]:
    """TODO"""
    interfaces: dict[str, TIFace] = {}
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()

    for iface, addrs in net_if_addrs.items():
        interfaces[iface] = {
            "is_up": net_if_stats[iface].isup if iface in net_if_stats else None,
            "details": [],
        }
        for addr in addrs:
            details: dict[str, Optional[str]] = {
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
            }
            interfaces[iface]["details"].append(details)
    return interfaces
