import time


class Factory:
    def __init__(self, id):
        self.id = id
        self.last_accessed = 0
        self.type = ""
        self.region = None
        self.owner = None
        self.level = 0
        self.wage = 0
        self.potential_wage = 0

    def set_last_accessed(self):
        self.last_accessed = time.time()

    def set_type(self, value):
        self.type = value

    def set_region(self, value):
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

    def __getstate__(self):
        return {
            "id": self.id,
            "last_accessed": self.last_accessed,
            "type": self.type,
            "region": self.region.id if self.region else None,
            "owner": self.owner.id if self.owner else None,
            "level": self.level,
            "wage": self.wage,
            "potential_wage": self.potential_wage,
        }
