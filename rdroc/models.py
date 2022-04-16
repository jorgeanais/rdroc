from dataclasses import dataclass, field
from tqdm import tqdm

from astropy.coordinates import SkyCoord
from astropy import table


@dataclass(frozen=True)
class StarCluster:
    """A Star Cluster representation."""

    name: str
    coordinates: SkyCoord
    data: table.Table


@dataclass
class Catalog:
    """A catalog representation."""

    name: str
    cds_id: str
    author: str
    params_table: table.Table = field(repr=False)
    members_table: table.Table = field(repr=False)
    star_clusters: dict[str, StarCluster] = field(
        init=False, default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        self.create_star_clusters()

    def create_star_clusters(self) -> None:
        clusters = table.unique(self.members_table, keys="Cluster")["Cluster"].data.data
        print(f"Creating {self.name} star clusters...")
        for cl in tqdm(clusters):
            members = self.members_table[self.members_table["Cluster"] == cl].copy()
            params = self.params_table[self.params_table["Cluster"] == cl]
            coords = SkyCoord(
                params["RA_ICRS"].data.data,
                params["DE_ICRS"].data.data,
                frame="icrs",
                unit="deg",
            )
            sc = StarCluster(cl, coords, members)
            self.star_clusters[cl] = sc
