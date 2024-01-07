players = {}
states = {}
autonomies = {}
regions = {}
parties = {}
factories = {}
blocs = {}
wars = {}


def get_player(id):
    from .player import Player

    id = int(id)
    if id in players:
        return players[id]
    else:
        players[id] = Player(id)
        return players[id]


def get_state(id):
    from .state import State

    id = int(id)
    if id in states:
        return states[id]
    else:
        states[id] = State(id)
        return states[id]


def get_autonomy(id):
    from .autonomy import Autonomy

    id = int(id)
    if id in autonomies:
        return autonomies[id]
    else:
        autonomies[id] = Autonomy(id)
        return autonomies[id]


def get_region(id):
    from .region import Region

    id = int(id)
    if id in regions:
        return regions[id]
    else:
        regions[id] = Region(id)
        return regions[id]


def get_party(id):
    from .party import Party

    id = int(id)
    if id in parties:
        return parties[id]
    else:
        parties[id] = Party(id)
        return parties[id]


def get_factory(id):
    from .factory import Factory

    id = int(id)
    if id in factories:
        return factories[id]
    else:
        factories[id] = Factory(id)
        return factories[id]


def get_bloc(id):
    from .bloc import Bloc

    id = int(id)
    if id in blocs:
        return blocs[id]
    else:
        blocs[id] = Bloc(id)
        return blocs[id]


def get_war(id):
    from .war import War

    id = int(id)
    if id in wars:
        return wars[id]
    else:
        wars[id] = War(id)
        return wars[id]
