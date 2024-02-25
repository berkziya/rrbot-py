import time

from models import get_state


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
            "time": self.last_accessed,
            "states": [state.id for state in self.states],
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.last_accessed = state["time"]
        self.states = [get_state(state) for state in state["states"]]
