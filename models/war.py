import time


from models import get_player, get_region

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.region import Region
    from models.player import Player


class War:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.type: str = None
        self.ending_time: float = None
        self.attacking_region: Region = None
        self.defending_region: Region = None
        self.attackers: dict[Player, int] = {}
        self.defenders: dict[Player, int] = {}
        self.attacker_damage: int = 0
        self.defender_damage: int = 0

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_type(self, value: str):
        self.type = value

    def set_ending_time(self, value: float):
        self.ending_time = value

    def set_attacking_region(self, value):
        self.attacking_region = value

    def set_defending_region(self, value):
        self.defending_region = value

    def set_attackers(self, value):
        self.attackers = value

    def set_defenders(self, value):
        self.defenders = value

    def set_attacker_damage(self, value: int):
        self.attacker_damage = value

    def set_defender_damage(self, value: int):
        self.defender_damage = value

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "type": self.type,
            "end": self.ending_time,
            "att": (self.attacking_region.id if self.attacking_region else None),
            "def": (self.defending_region.id if self.defending_region else None),
            "atts": {k.id: v for k, v in self.attackers.items()},
            "defs": {k.id: v for k, v in self.defenders.items()},
            "attdmg": self.attacker_damage,
            "defdmg": self.defender_damage,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.last_accessed = state.get("time")
        self.type = state.get("type")
        self.ending_time = state.get("end")
        self.attacking_region = (
            get_region(state.get("att")) if state.get("att") else None
        )
        self.defending_region = (
            get_region(state.get("def")) if state.get("def") else None
        )
        self.attackers = {get_player(k): v for k, v in state.get("atts", {}).items()}
        self.defenders = {get_player(k): v for k, v in state.get("defs", {}).items()}
        self.attacker_damage = state.get("attdmg")
        self.defender_damage = state.get("defdmg")
