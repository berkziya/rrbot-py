import time


from models import get_autonomy, get_player, get_region

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.autonomy import Autonomy
    from models.region import Region
    from models.player import Player
    from models.war import War


class State:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.leader: Player = None
        self.economics: Player = None
        self.foreign: Player = None
        self.form: str = ""
        self.autonomies: list[Autonomy] = []
        self.regions: list[Region] = []
        self.num_of_regions: int = 0
        self.citizens: list[Player] = []
        self.num_of_citizens: int = 0
        self.residents: list[Player] = []
        self.num_of_residents: int = 0
        self.budget: dict[str, int] = {
            "money": 0,
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.wars: list[War] = []
        self.num_of_wars: int = 0
        self.borders: str = ""

    def set_name(self, value):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_leader(self, value):
        self.leader = value

    def set_economics(self, value):
        self.economics = value

    def set_foreign(self, value):
        self.foreign = value

    def set_form(self, value):
        self.form = value

    def set_budget(self, element, value, what="="):
        if what == "=":
            self.budget[element] = value
        elif what == "+":
            from misc.utils import sum_costs

            self.budget = sum_costs(self.budget, {element: value})
        elif what == "-":
            from misc.utils import subtract_costs

            self.budget = subtract_costs(self.budget, {element: value})

    def set_budgets(self, value, what="="):
        if what == "=":
            self.budget = value
        elif what == "+":
            from misc.utils import sum_costs

            self.budget = sum_costs(self.budget, value)
        elif what == "-":
            from misc.utils import subtract_costs

            self.budget = subtract_costs(self.budget, value)

    def set_borders(self, value):
        self.borders = value

    def set_wars(self, value):
        self.wars = value

    def add_war(self, value):
        if value not in self.wars:
            self.wars.append(value)

    def set_num_of_wars(self, value):
        self.num_of_wars = value

    def set_regions(self, value):
        self.regions = value

    def add_region(self, value):
        if value not in self.regions:
            self.regions.append(value)

    def set_num_of_regions(self, value):
        self.num_of_regions = value

    @property
    def power_production(self) -> int:
        production = 0
        for region in self.regions:
            production += region.power_production
        return production

    @property
    def power_consumption(self) -> int:
        consumption = 0
        for region in self.regions:
            consumption += region.power_consumption
        return consumption

    def set_citizens(self, value):
        self.citizens = value

    def set_num_of_citizens(self, value):
        self.num_of_citizens = value

    def set_residents(self, value):
        self.residents = value

    def set_num_of_residents(self, value):
        self.num_of_residents = value

    def set_autonomies(self, value):
        self.autonomies = value

    def add_autonomy(self, value):
        if value not in self.autonomies:
            self.autonomies.append(value)

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "lead": self.leader.id if self.leader else None,
            "econ": self.economics.id if self.economics else None,
            "foreign": self.foreign.id if self.foreign else None,
            "form": self.form,
            "autonomies": [x.id for x in self.autonomies],
            "regions": [x.id for x in self.regions],
            "citizens": [x.id for x in self.citizens],
            "residents": [x.id for x in self.residents],
            "budget": self.budget,
            "borders": self.borders,
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.leader = get_player(state.get("lead"))
        self.economics = get_player(state.get("econ"))
        self.foreign = get_player(state.get("foreign"))
        self.form = state.get("form")
        self.autonomies = [get_autonomy(x) for x in state.get("autonomies", [])]
        self.regions = [get_region(x) for x in state.get("regions", [])]
        self.citizens = [get_player(x) for x in state.get("citizens", [])]
        self.residents = [get_player(x) for x in state.get("residents", [])]
        self.budget = state.get("budget", {})
        self.borders = state.get("borders")
