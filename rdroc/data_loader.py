from dataclasses import field
from pathlib import Path
import pickle
import pydantic
from pydantic.dataclasses import dataclass
import yaml

from astroquery.utils.commons import TableList
from astroquery.vizier import Vizier

from rdroc.settings import Config
from rdroc.models import Catalog


Vizier.ROW_LIMIT = -1


@dataclass
class StagingCatalog:
    """Staging class for validation of catalogs in yaml file."""

    name: str
    cds_id: str
    author: str
    table_names: dict[str, str]
    tablelist_path: Path = field(init=False, default_factory=Path)

    @pydantic.validator("table_names")
    def check_tables_key(cls, value):
        table_keys = ("clusters_params", "cluster_members")
        if not all(key in value for key in table_keys):
            raise ValueError(f"Catalog must include {', '.join(table_keys)}.")
        return value

    def __post_init_post_parse__(self):
        self.tablelist_path = Config.RAW_DATA / (
            self.name + self.cds_id.replace("/", "_") + ".pkl"
        )
        # Add cds_id to table_names
        self.table_names = {
            k: self.cds_id + "/" + v for k, v in self.table_names.items()
        }


class DataLoader:
    def __init__(self) -> None:
        self.staging_list: list[StagingCatalog] = []
        self.catalogs: list[Catalog] = []

    def read_input_catalog_file(self) -> None:
        with open(Config.CATALOGS) as file:
            file_content = yaml.load(file, Loader=yaml.FullLoader)
            self.staging_list = [StagingCatalog(**c) for c in file_content]

    def download_tablelist(self, staging_catalog: StagingCatalog) -> TableList:
        return Vizier.get_catalogs(staging_catalog.cds_id)

    def save_tablelist(self, table_list: TableList, path: Path) -> None:
        with open(str(path), "wb") as file:
            pickle.dump(table_list, file)

    def read_tablelist(self, path: Path) -> TableList:
        with open(str(path), "r") as file:
            return pickle.load(file)

    def load_catalogs(self) -> None:
        for sc in self.staging_list:
            if sc.tablelist_path.is_file():
                tl = self.read_tablelist(sc.tablelist_path)
            else:
                tl = self.download_tablelist(sc)

            p_table = tl[sc.table_names["clusters_params"]]
            m_table = tl[sc.table_names["cluster_members"]]
            c = Catalog(sc.name, sc.cds_id, sc.author, p_table, m_table)
            self.catalogs.append(c)

    def run(self) -> None:
        self.read_input_catalog_file()
        self.load_catalogs()
