import time

from models import get_player, get_region

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.region import Region


class Party:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.leader: Player = None
        self.region: Region = None
        self.secretaries: list[Player] = []
        self.members: list[Player] = []

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_leader(self, value):
        self.leader = value

    def set_region(self, value):
        self.region = value

    def set_secretaries(self, value):
        self.secretaries = value

    def set_members(self, value):
        self.members = value

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "leader": self.leader.id if self.leader else None,
            "region": self.region.id if self.region else None,
            "secs": [player.id for player in self.secretaries],
            "members": [player.id for player in self.members],
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.leader = get_player(state.get("leader"))
        self.region = get_region(state.get("region"))
        self.secretaries = [get_player(player) for player in state.get("secs", [])]
        self.members = [get_player(player) for player in state.get("members", [])]
