import time

from models import get_state

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.state import State


class Bloc:
    def __init__(self, id):
        self.id: int = id
        self.name: str | int = self.id
        self.last_accessed: int = 0
        self.states: list[State] = []

    def set_name(self, value: str):
        self.name = value

    def set_last_accessed(self):
        self.last_accessed = int(time.time())

    def set_states(self, value):
        self.members = value

    def add_state(self, value):
        if value not in self.states:
            self.states.append(value)

    def __str__(self):
        return str(self.name)

    def __getstate__(self):
        return {
            "id": self.id,
            "time": self.last_accessed,
            "states": [state.id for state in self.states],
        }

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name = state.get("name", self.id)
        self.last_accessed = state.get("time")
        self.states = [get_state(state) for state in state.get("states", [])]
