import re
from collections import defaultdict


def dotless(number):
    numbers = re.findall(r"\d+", number)
    return int("".join(numbers)) if numbers else 0


def numba(number):
    units = ["", "k", "kk", "k" + "kk", "T", "P"]
    for unit in units:
        if abs(number) < 1000:
            return f"{number:.1f}{unit}"
        number /= 1000
    return f"{number:.3f}{unit}"


def time_to_secs(time_str):
    days, hours, minutes, seconds = 0, 0, 0, 0
    if " d " in time_str:
        days_str, time_str = time_str.split(" d ")
        days = int(days_str)
    time_parts = time_str.split(":")
    if len(time_parts) == 3:
        hours, minutes, seconds = map(int, time_parts)
    elif len(time_parts) == 2:
        minutes, seconds = map(int, time_parts)
    elif len(time_parts) == 1:
        seconds = int(time_parts[0])
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds + 1
    return total_seconds


def sum_costs(cost1, cost2):
    costs = defaultdict(int, cost1)
    for key, value in cost2.items():
        costs[key] += value
    return {key: value for key, value in costs.items() if value > 0}


def subtract_costs(cost1, cost2):
    costs = defaultdict(int, cost1)
    for key, value in cost2.items():
        costs[key] -= value
    return {key: value for key, value in costs.items() if value > 0}
