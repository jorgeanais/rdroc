from dataclasses import dataclass, field

from astropy.coordinates import SkyCoord
from astropy.table import Table


@dataclass
class StarCluster:
    """A Star Cluster representation."""

    name: str
    coordinates: SkyCoord
    data: Table


@dataclass
class Catalog:
    """A catalog representation."""

    name: str
    cds_id: str
    author: str
    params_table: Table
    members_table: Table
    star_clusters: dict[str, StarCluster] = field(init=False, default_factory=dict)

    def __post_init__(self):
        pass

    def create_star_clusters(self):
        pass
