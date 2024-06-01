import time

from models import get_autonomy, get_party, get_player, get_region, get_state

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.autonomy import Autonomy
    from models.party import Party
    from models.region import Region
    from models.state import State


class Player:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.premium: bool = True
        self.level: int = 0
        self.money: dict[str, int] = {"money": 0, "gold": 0}
        self.current_energy: int = 0
        self.storage: dict[str, int] = {}
        self.state_leader: Player = None
        self.rating: int = 0
        self.perks: dict[str, int] = {"str": 0, "edu": 0, "end": 0}
        self.region: Region = None
        self.residency: Player = None
        self.workpermits: dict[State, Region] = {}
        self.governor: Autonomy | Region = None
        self.economics: State = None
        self.foreign: State = None
        self.party: Party = None

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_premium(self, value: bool):
        self.premium = value

    def set_level(self, value: int):
        self.level = value

    def set_money(self, element: str, value: int):
        self.money[element] = value

    def set_current_energy(self, value: int):
        self.current_energy = value

    def set_storage(self, element: str, value: int):
        self.storage[element] = value

    def set_state_leader(self, value):
        self.state_leader = value

    def set_rating(self, value: int):
        self.rating = value

    def set_perk(self, element, value: int):
        self.perks[element] = value

    def set_perks(self, str, edu, end):
        self.perks["str"] = str
        self.perks["edu"] = edu
        self.perks["end"] = end

    def set_region(self, value):
        self.region = value

    def set_residency(self, value):
        self.residency = value

    def set_workpermits(self, value):
        self.workpermits = value

    def set_governor(self, value):
        self.governor = value

    def set_economics(self, value):
        self.economics = value

    def set_foreign(self, value):
        self.foreign = value

    def set_party(self, value):
        self.party = value

    FULL_ENERGY = 300

    def alpha(self, energy=FULL_ENERGY) -> int:
        slot = energy // 6
        return 50 * (self.level + 20) * slot

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "level": self.level,
            "lead": self.state_leader.id if self.state_leader else None,
            "perks": self.perks,
            "region": self.region.id if self.region else None,
            "residency": self.residency.id if self.residency else None,
            "wperm": {
                key.id: (value.id if value else 0)
                for key, value in self.workpermits.items()
            },
            "governor": self.governor.id if self.governor else None,
            "econ": self.economics.id if self.economics else None,
            "foreign": self.foreign.id if self.foreign else None,
            "party": self.party.id if self.party else None,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.level = state.get("level")
        self.state_leader = get_player(state.get("lead"))
        self.perks = state.get("perks")
        self.region = get_region(state.get("region"))
        self.residency = get_region(state.get("residency"))
        self.workpermits = {
            get_state(key): (get_region(value) if value else 0)
            for key, value in state.get("wperm", {}).items()
        }
        self.governor = get_autonomy(state.get("governor"))
        self.economics = get_state(state.get("econ"))
        self.foreign = get_state(state.get("foreign"))
        self.party = get_party(state.get("party"))
