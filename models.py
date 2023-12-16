import time


class Player:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.level = 0
        self.money = {"money": 0, "gold": 0, "energy": 0}
        self.state_leader = None
        self.commander = None
        self.rating = 0
        self.perks = {"str": 0, "edu": 0, "end": 0}
        self.region = None
        self.state = None
        self.residency = None
        self.workpermits = {}
        self.governor = None
        self.economics = None
        self.foreign = None
        self.party = None

    def set_level(self, value):
        self.level = value

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_money(self, element, value):
        self.money[element] = value

    def set_state_leader(self, value):
        self.state_leader = value

    def set_commander(self, value):
        self.commander = value

    def set_rating(self, value):
        self.rating = value

    def set_perk(self, element, value):
        self.perks[element] = value

    def set_perks(self, str, edu, end):
        self.perks["str"] = str
        self.perks["edu"] = edu
        self.perks["end"] = end

    def set_region(self, value):
        self.region = value

    def set_state(self, value):
        self.state = value

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

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "level": self.level,
            "money": self.money,
            "state_leader": self.state_leader.id if self.state_leader else None,
            "commander": self.commander.id if self.commander else None,
            "rating": self.rating,
            "perks": self.perks,
            "region": self.region.id if self.region else None,
            "state": self.state.id if self.state else None,
            "residency": self.residency.id if self.residency else None,
            "workpermits": {
                key.id: (value.id if value else 0)
                for key, value in self.workpermits.items()
            },
            "governor": self.governor.id if self.governor else None,
            "economics": self.economics.id if self.economics else None,
            "foreign": self.foreign.id if self.foreign else None,
            "party": self.party.id if self.party else None,
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.level = state["level"]
        self.money = state["money"]
        self.state_leader = (
            get_player(state["state_leader"]) if state["state_leader"] else None
        )
        self.commander = get_player(state["commander"]) if state["commander"] else None
        self.rating = state["rating"]
        self.perks = state["perks"]
        self.region = get_region(state["region"]) if state["region"] else None
        self.state = get_state(state["state"]) if state["state"] else None
        self.residency = get_region(state["residency"]) if state["residency"] else None
        self.workpermits = {
            get_state(key): (get_region(value) if value else 0)
            for key, value in state["workpermits"].items()
        }
        self.governor = get_autonomy(state["governor"]) if state["governor"] else None
        self.economics = get_state(state["economics"]) if state["economics"] else None
        self.foreign = get_state(state["foreign"]) if state["foreign"] else None
        self.party = get_party(state["party"]) if state["party"] else None


class State:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.leader = None
        self.commander = None
        self.economics = None
        self.foreign = None
        self.government_form = ""
        self.autonomies = []
        self.regions = []
        self.num_of_regions = 0
        self.citizens = []
        self.num_of_citizens = 0
        self.residents = []
        self.num_of_residents = 0
        self.budget = {
            "money": 0,
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.wars = []
        self.num_of_wars = 0
        self.borders = ""

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_leader(self, value):
        self.leader = value

    def set_commander(self, value):
        self.commander = value

    def set_economics(self, value):
        self.economics = value

    def set_foreign(self, value):
        self.foreign = value

    def set_government_form(self, value):
        self.government_form = value

    def set_budget(self, element, value):
        self.budget[element] = value

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
        return str(self.id)


class Autonomy:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.state = None
        self.governor = None
        self.regions = []
        self.budget = {
            "money": 0,
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_state(self, value):
        self.state = value

    def set_governor(self, value):
        self.governor = value

    def set_regions(self, value):
        self.regions = value

    def add_region(self, value):
        if value not in self.regions:
            self.regions.append(value)

    def set_budget(self, element, value):
        self.budget[element] = value

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "state": self.state.id if self.state else None,
            "governor": self.governor.id if self.governor else None,
            "regions": [region.id for region in self.regions],
            "budget": self.budget,
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.state = get_state(state["state"]) if state["state"] else None
        self.governor = get_player(state["governor"]) if state["governor"] else None
        self.regions = [get_region(region) for region in state["regions"]]
        self.budget = state["budget"]


class Region:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.state = None
        self.autonomy = None
        self.location = [0, 0]
        self.buildings = {
            "hospital": 0,
            "military": 0,
            "school": 0,
            "missile system": 0,
            "sea port": 0,
            "power plant": 0,
            "space port": 0,
            "airport": 0,
            "homes": 0,
        }
        self.rating = 0
        self.residents = []
        self.num_of_residents = 0
        self.citizens = []
        self.num_of_citizens = 0
        self.initial_attack_damage = 0
        self.initial_defend_damage = 0
        self.tax = 0
        self.market_tax = 0
        self.sea_access = False
        self.resources = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.deep_resources = {
            "gold": 0,
            "oil": 0,
            "ore": 0,
            "uranium": 0,
            "diamonds": 0,
        }
        self.indexes = {
            "health": 0,
            "military": 0,
            "education": 0,
            "development": 0,
        }
        self.border_regions = []
        self.factories = []

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_state(self, value):
        self.state = value

    def set_autonomy(self, value):
        self.autonomy = value

    def set_location(self, value):
        self.location = value

    def set_buildings(self, element, value):
        self.buildings[element] = value

    def set_rating(self, value):
        self.rating = value

    def set_residents(self, value):
        self.residents = value

    def set_num_of_residents(self, value):
        self.num_of_residents = value

    def set_citizens(self, value):
        self.citizens = value

    def set_num_of_citizens(self, value):
        self.num_of_citizens = value

    def set_initial_attack_damage(self, value):
        self.initial_attack_damage = value

    def set_initial_defend_damage(self, value):
        self.initial_defend_damage = value

    def set_tax(self, value):
        self.tax = value

    def set_market_tax(self, value):
        self.market_tax = value

    def set_sea_access(self, value):
        self.sea_access = value

    def set_resources(self, element, value):
        self.resources[element] = value

    def set_deep_resources(self, element, value):
        self.deep_resources[element] = value

    def set_indexes(self, element, value):
        self.indexes[element] = value

    def set_border_regions(self, value):
        self.border_regions = value

    def add_border_region(self, value):
        if value not in self.border_regions:
            self.border_regions.append(value)

    def set_factories(self, value):
        self.factories = value

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "state": self.state.id if self.state else None,
            "autonomy": self.autonomy.id if self.autonomy else None,
            "location": self.location,
            "buildings": self.buildings,
            "rating": self.rating,
            "residents": [player.id for player in self.residents],
            "num_of_residents": self.num_of_residents,
            "citizens": [player.id for player in self.citizens],
            "num_of_citizens": self.num_of_citizens,
            "initial_attack_damage": self.initial_attack_damage,
            "initial_defend_damage": self.initial_defend_damage,
            "tax": self.tax,
            "market_tax": self.market_tax,
            "sea_access": self.sea_access,
            "resources": self.resources,
            "deep_resources": self.deep_resources,
            "indexes": self.indexes,
            "border_regions": [region.id for region in self.border_regions],
            "factories": [factory.id for factory in self.factories],
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.state = get_state(state["state"]) if state["state"] else None
        self.autonomy = get_autonomy(state["autonomy"]) if state["autonomy"] else None
        self.location = state["location"]
        self.buildings = state["buildings"]
        self.rating = state["rating"]
        self.residents = [get_player(player) for player in state["residents"]]
        self.num_of_residents = state["num_of_residents"]
        self.citizens = [get_player(player) for player in state["citizens"]]
        self.num_of_citizens = state["num_of_citizens"]
        self.initial_attack_damage = state["initial_attack_damage"]
        self.initial_defend_damage = state["initial_defend_damage"]
        self.tax = state["tax"]
        self.market_tax = state["market_tax"]
        self.sea_access = state["sea_access"]
        self.resources = state["resources"]
        self.deep_resources = state["deep_resources"]
        self.indexes = state["indexes"]
        self.border_regions = [get_region(region) for region in state["border_regions"]]
        self.factories = [get_factory(factory) for factory in state["factories"]]


class Party:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.leader = None
        self.location = None
        self.secretaries = []
        self.members = []

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_leader(self, value):
        self.leader = value

    def set_location(self, value):
        self.location = value

    def set_secretaries(self, value):
        self.secretaries = value

    def set_members(self, value):
        self.members = value

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "leader": self.leader.id if self.leader else None,
            "location": self.location.id if self.location else None,
            "secretaries": [player.id for player in self.secretaries],
            "members": [player.id for player in self.members],
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.leader = get_player(state["leader"]) if state["leader"] else None
        self.location = get_region(state["location"]) if state["location"] else None
        self.secretaries = [get_player(player) for player in state["secretaries"]]
        self.members = [get_player(player) for player in state["members"]]


class Factory:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.type = ""
        self.location = None
        self.owner = None
        self.level = 0
        self.wage = 0
        self.potential_wage = 0

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_type(self, value):
        self.type = value

    def set_location(self, value):
        self.location = value

    def set_owner(self, value):
        self.owner = value

    def set_level(self, value):
        self.level = value

    def set_wage(self, value):
        self.wage = value

    def set_potential_wage(self, value):
        self.potential_wage = value

    def __str__(self):
        return str(self.id)


class Bloc:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.states = []

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_states(self, value):
        self.members = value

    def add_state(self, value):
        if value not in self.states:
            self.states.append(value)

    def __str__(self):
        return str(self.id)

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "states": [state.id for state in self.states],
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["last_accessed"]
        self.states = [get_state(state) for state in state["states"]]


players = {}
states = {}
autonomies = {}
regions = {}
parties = {}
factories = {}
blocs = {}


def get_player(id):
    id = int(id)
    if id in players:
        return players[id]
    else:
        players[id] = Player(id)
        return players[id]


def get_state(id):
    id = int(id)
    if id in states:
        return states[id]
    else:
        states[id] = State(id)
        return states[id]


def get_autonomy(id):
    id = int(id)
    if id in autonomies:
        return autonomies[id]
    else:
        autonomies[id] = Autonomy(id)
        return autonomies[id]


def get_region(id):
    id = int(id)
    if id in regions:
        return regions[id]
    else:
        regions[id] = Region(id)
        return regions[id]


def get_party(id):
    id = int(id)
    if id in parties:
        return parties[id]
    else:
        parties[id] = Party(id)
        return parties[id]


def get_factory(id):
    id = int(id)
    if id in factories:
        return factories[id]
    else:
        factories[id] = Factory(id)
        return factories[id]


def get_bloc(id):
    id = int(id)
    if id in blocs:
        return blocs[id]
    else:
        blocs[id] = Bloc(id)
        return blocs[id]
