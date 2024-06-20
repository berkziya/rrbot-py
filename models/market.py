class Market:
    def __init__(self):
        self.prices = {
            "money": [0.60],
            "gold": [2.5],
            "oil": [106],
            "ore": [98],
            "uranium": [920],
            "diamonds": [625e3],
            "lox": [2140],
            "helium3": [420e3],
            "rivalium": [70e3],
            "antirad": [2550e3],
            "spacerockets": [12e6],
            "lss": [84e6],
            "tanks": [5000],
            "aircrafts": [27e3],
            "missiles": [200e3],
            "bombers": [310e3],
            "battleships": [490e3],
            "laserdrones": [132e6],
            "moontanks": [300e3],
            "spacestations": [7e3],
        }

    def __getitem__(self, item):
        return self.prices[item][-1]

    def __setitem__(self, key, value):
        self.prices[key].append(value)
