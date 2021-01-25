from typing import NamedTuple


class IQAirDevice(NamedTuple):
    name: str
    placement: str
    location: str
    external: bool
