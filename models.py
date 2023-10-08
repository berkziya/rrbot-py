class Player:
    def __init__(self, id):
        self.id = id
        self.level = 0
        self.money = {'money':0, 'gold':0, 'energy':0}
        self.state_leader = None
        self.commander = None
        self.rating = 0
        self.perks = {'str':0, 'edu':0, 'end':0}
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
        self.perks['str'] = str
        self.perks['edu'] = edu
        self.perks['end'] = end
    
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

players = {0: Player(0)}

def get_player(id):
    if id in players:
        return players[id]
    else:
        player = Player(id)
        players[id] = player
        return player


class State:
    def __init__(self, id):
        self.id = id
        self.leader = None
        self.commander = None
        self.economics = None
        self.foreign = None
        self.government_form = ''
        self.autonomies = []
        self.regions = []
        self.num_of_regions = 0
        self.citizens = []
        self.num_of_citizens = 0
        self.residents = []
        self.num_of_residents = 0
        self.budget = {'money': 0, 'gold': 0, 'oil': 0, 'ore': 0, 'uranium': 0, 'diamonds': 0}
        self.wars = []
        self.borders = ''

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
    
    def set_budget(self, money, gold, oil, ore, uranium, diamonds):
        self.budget['money'] = money
        self.budget['gold'] = gold
        self.budget['oil'] = oil
        self.budget['ore'] = ore
        self.budget['uranium'] = uranium
        self.budget['diamonds'] = diamonds
    
    def set_borders(self, value):
        self.borders = value
    
    def set_wars(self, value):
        self.wars = value
    
    def add_war(self, value):
        self.wars.append(value)
    
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
        self.governor = players[0]
        self.regions = []
        self.budget = {'money': 0, 'gold': 0, 'oil': 0, 'ore': 0, 'uranium': 0, 'diamonds': 0}
    
    def set_governor(self, value):
        self.governor = value
    
    def set_regions(self, value):
        self.regions = value
    
    def set_budget(self, money, gold, oil, ore, uranium, diamonds):
        self.budget['money'] = money
        self.budget['gold'] = gold
        self.budget['oil'] = oil
        self.budget['ore'] = ore
        self.budget['uranium'] = uranium
        self.budget['diamonds'] = diamonds
    
    def __str__(self):
        return str(self.id)

class Region:
    def __init__(self, id):
        self.id = id
        self.state = None
        self.autonomy = None
        self.residents = []
        self.num_of_residents = 0
        self.citizens = []
        self.num_of_citizens = 0
    
    def set_state(self, value):
        self.state = value
    
    def set_autonomy(self, value):
        self.autonomy = value
    
    def set_residents(self, value):
        self.residents = value
    
    def set_num_of_residents(self, value):
        self.num_of_residents = value
    
    def set_citizens(self, value):
        self.citizens = value
    
    def set_num_of_citizens(self, value):
        self.num_of_citizens = value
    
    def __str__(self):
        return str(self.id)

states = {0: State(0)}
autonomies = {0: Autonomy(0)}
regions = {0: Region(0)}

def get_state(id):
    if id in states:
        return states[id]
    else:
        state = State(id)
        states[id] = state
        return state

def get_region(id):
    if id in regions:
        return regions[id]
    else:
        region = Region(id)
        regions[id] = region
        return region

def get_autonomy(id):
    if id in autonomies:
        return autonomies[id]
    else:
        autonomy = Autonomy(id)
        autonomies[id] = autonomy
        return autonomy


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

parties = {0: Party(0)}

def get_party(id):
    if id in parties:
        return parties[id]
    else:
        party = Party(id)
        parties[id] = party
        return party