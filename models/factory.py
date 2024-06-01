import time

from misc.utils import dotless
from models import get_player, get_region

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.region import Region


class Factory:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.type: str = ""
        self.region: Region = None
        self.owner: Player = None
        self.level: int = 0
        self.wage: float = 0
        self.fixed_wage: bool = False
        self.potential_wage: int = 0

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_type(self, value: str):
        if value == "diamond":
            value = "diamonds"
        if value == "liquefaction":
            value = "lox"
        if "helium" in value:
            value = "helium3"
        self.type = value

    def set_region(self, value):
        self.region = value

    def set_owner(self, value):
        self.owner = value

    def set_level(self, value: int):
        self.level = value

    def set_wage(self, value: str):
        if "%" in value:
            self.fixed_wage = False
            value = dotless(value) / 100
        else:
            self.fixed_wage = True
            value = dotless(value)
        self.wage = value

    def get_wage(self) -> float:
        return self.wage if self.fixed_wage else self.wage * (self.level**0.8)

    def set_fixed_wage(self, value: bool):
        self.fixed_wage = value

    def set_potential_wage(self, value: int):
        self.potential_wage = value

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "time": self.last_accessed,
            "type": self.type,
            "region": self.region.id if self.region else None,
            "owner": self.owner.id if self.owner else None,
            "level": self.level,
            "wage": self.wage,
            "fwage": self.fixed_wage,
            "pwage": self.potential_wage,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.type = state.get("type")
        self.region = get_region(state.get("region"))
        self.owner = get_player(state.get("owner"))
        self.level = state.get("level")
        self.wage = state.get("wage")
        self.fixed_wage = state.get("fwage")
        self.potential_wage = state.get("pwage")
