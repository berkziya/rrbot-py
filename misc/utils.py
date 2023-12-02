import re


def dotless(number):
    numbers = re.findall(r"\d+", number)
    return int("".join(numbers)) if numbers else 0


def k(number):
    if number < 1e3:
        return number
    return str(number)[:-3] + " k"


def kk(number):
    if number < 1e6:
        return k(number)
    return str(number)[:-6] + " kk"


def numba(number):
    if number < 1e9:
        return kk(number)
    if number > 1e13:
        return str(number)[:-12] + " t"
    return str(number)[:-9] + " kkk"


def timetosecs(time):
    days = 0
    if " d " in time:
        days = int(time.split(" d ")[0])
        time = time.split(" d ")[1]
    time = time.split(":")
    hours = 0
    if len(time) == 3:
        hours = int(time.pop(0))
    minutes = int(time[0])
    seconds = int(time[1])
    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds + 3
    return total_seconds


def sum_costs(cost1, cost2):
    costs = {
        key: cost1.get(key, 0) + cost2.get(key, 0) for key in set(cost1) | set(cost2)
    }
    if not costs == {}:
        costs = {key: value for key, value in costs.items() if value > 0}
    return costs


def subtract_costs(cost1, cost2):
    costs = {
        key: cost1.get(key, 0) - cost2.get(key, 0) for key in set(cost1) | set(cost2)
    }
    if not costs == {}:
        costs = {key: value for key, value in costs.items() if value > 0}
    return costs
