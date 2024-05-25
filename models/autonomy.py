import time

from models import get_player, get_region, get_state
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.region import Region
    from models.state import State


class Autonomy:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.state: State = None
        self.governor: Player = None
        self.regions: list[Region] = []
        self.budget: dict[str:int] = {
            "money": 0,
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_state(self, value):
        self.state = value

    def set_governor(self, value):
        self.governor = value

    def set_regions(self, value):
        self.regions = value

    def add_region(self, value):
        if value not in self.regions:
            self.regions.append(value)

    def set_budget(self, element: str, value: int):
        self.budget[element] = value

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "state": self.state.id if self.state else None,
            "governor": self.governor.id if self.governor else None,
            "regions": [region.id for region in self.regions],
            "budget": self.budget,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.state = get_state(state.get("state"))
        self.governor = get_player(state.get("governor"))
        self.regions = [get_region(region) for region in state.get("regions", [])]
        self.budget = state.get("budget", {})
