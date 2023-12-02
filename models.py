class Player:
    def __init__(self, id):
        self.id = id
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


class State:
    def __init__(self, id):
        self.id = id
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
        self.wars.append(value)

    def set_num_of_wars(self, value):
        self.num_of_wars = value

    def set_regions(self, value):
        self.regions = value

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

    def __str__(self):
        return str(self.id)


class Autonomy:
    def __init__(self, id):
        self.id = id
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

    def set_state(self, value):
        self.state = value

    def set_governor(self, value):
        self.governor = value

    def set_regions(self, value):
        self.regions = value

    def set_budget(self, element, value):
        self.budget[element] = value

    def __str__(self):
        return str(self.id)


class Region:
    def __init__(self, id):
        self.id = id
        self.state = None
        self.autonomy = None
        self.location = (0, 0)
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

    def set_factories(self, value):
        self.factories = value

    def __str__(self):
        return str(self.id)


class Party:
    def __init__(self, id):
        self.id = id
        self.leader = None
        self.location = None
        self.secretaries = []
        self.members = []

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


class Factory:
    def __init__(self, id):
        self.id = id
        self.type = ""
        self.location = None
        self.owner = None
        self.level = 0
        self.wage = 0
        self.potential_wage = 0

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


players = {}
states = {}
autonomies = {}
regions = {}
parties = {}
factories = {}


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
