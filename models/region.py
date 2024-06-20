from __future__ import annotations
import time


from models import get_autonomy, get_factory, get_player, get_region, get_state

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.autonomy import Autonomy
    from models.factory import Factory
    from models.player import Player
    from models.state import State


class Region:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.state: State = None
        self.autonomy: Autonomy = None
        self.buildings: dict[str, int] = {
            "macademy": 0,
            "hospital": 0,
            "military": 0,
            "school": 0,
            "missile": 0,
            "sea": 0,
            "power": 0,
            "spaceport": 0,
            "airport": 0,
            "homes": 0,
        }
        self.rating: int = 0
        self.residents: list[Player] = []
        self.num_of_residents: int = 0
        self.citizens: list[Player] = []
        self.num_of_citizens: int = 0
        self.tax: float = 0
        self.market_tax: float = 0
        self.sea_access: bool = False
        self.resources: dict[str, int] = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.deep_resources: dict[str, int] = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.indexes: dict[str, int] = {
            "hospital": 0,
            "military": 0,
            "school": 0,
            "homes": 0,
        }
        self.border_regions: list[Region] = []
        self.factories: list[Factory] = []

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_state(self, value):
        self.state = value

    def set_autonomy(self, value):
        self.autonomy = value

    def set_buildings(self, element: str, value: int):
        self.buildings[element] = value

    @property
    def power_consumption(self) -> int:
        return (
            self.buildings["hospital"]
            + self.buildings["military"]
            + self.buildings["school"]
            + self.buildings["missile"]
            + self.buildings["sea"]
            + self.buildings["spaceport"]
            + self.buildings["airport"]
        ) * 2

    @property
    def power_production(self) -> int:
        return self.buildings["power"] * 10

    def set_rating(self, value: int):
        self.rating = value

    def set_residents(self, value):
        self.residents = value

    def set_num_of_residents(self, value: int):
        self.num_of_residents = value

    def set_citizens(self, value):
        self.citizens = value

    def set_num_of_citizens(self, value: int):
        self.num_of_citizens = value

    @property
    def initial_attack_damage(self) -> int:
        return self.buildings["macademy"] * 900_000

    @property
    def initial_defend_damage(self) -> int:
        return (
            self.buildings["hospital"]
            + 2 * self.buildings["military"]
            + self.buildings["school"]
            + self.buildings["missile"]
            + self.buildings["sea"]
            + self.buildings["power"]
            + self.buildings["spaceport"]
            + self.buildings["airport"]
        ) * 100_000

    def set_tax(self, value: float):
        self.tax = value

    def set_market_tax(self, value: float):
        self.market_tax = value

    def set_sea_access(self, value: bool):
        self.sea_access = value

    def set_resources(self, element: str, value: int):
        self.resources[element] = value

    def set_deep_resources(self, element: str, value: int):
        self.deep_resources[element] = value

    def set_indexes(self, element: str, value: int):
        self.indexes[element] = value

    def set_border_regions(self, value):
        self.border_regions = value

    def add_border_region(self, value):
        if value not in self.border_regions:
            self.border_regions.append(value)

    def set_factories(self, value):
        self.factories = value

    def add_factory(self, value):
        if value not in self.factories:
            self.factories.append(value)

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "state": self.state.id if self.state else None,
            "autonomy": self.autonomy.id if self.autonomy else None,
            "buildings": self.buildings,
            "rating": self.rating,
            "residents": [player.id for player in self.residents],
            "citizens": [player.id for player in self.citizens],
            "tax": self.tax,
            "mtax": self.market_tax,
            "sea": self.sea_access,
            "indexes": self.indexes,
            "border_regs": [region.id for region in self.border_regions],
            "factories": [factory.id for factory in self.factories],
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.state = get_state(state.get("state"))
        self.autonomy = get_autonomy(state.get("autonomy"))
        self.buildings = state.get("buildings")
        self.rating = state.get("rating")
        self.residents = [get_player(player) for player in state.get("residents", [])]
        self.citizens = [get_player(player) for player in state.get("citizens", [])]
        self.tax = state.get("tax")
        self.market_tax = state.get("mtax")
        self.sea_access = state.get("sea")
        self.indexes = state.get("indexes")
        self.border_regions = [
            get_region(region) for region in state.get("border_regs", [])
        ]
        self.factories = [
            get_factory(factory) for factory in state.get("factories", [])
        ]
