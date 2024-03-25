import re
from collections import defaultdict
from datetime import datetime, timedelta


def dotless(number):
    numbers = re.findall(r"\d+", number)
    return int("".join(numbers)) if numbers else 0


def num_to_slang(number):
    units = ["", "k", "kk", "k" + "kk", "T", "P"]
    for unit in units:
        if abs(number) < 1000:
            return f"{number:.1f}{unit}"
        number /= 1000
    return f"{number:.3f}{unit}"


def slang_to_num(slang):
    if isinstance(slang, int):
        return slang
    slang = slang.lower().strip().replace(",", "").replace(" ", "").replace(".", "")
    while slang.endswith("k"):
        slang = slang[:-1] + "000"
    while slang.endswith("t"):
        slang = slang[:-1] + "0" * 12
    return int(slang)


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


def get_ending_timestamp(text):
    match = re.search(r"((\w+ \d+:\d+)|(\d+ \w+ \d+ \d+:\d+))", text)
    if match:
        date_time_str = match.group(1)
        if "today" in date_time_str:
            date_time_str = date_time_str.replace(
                "today", datetime.now().strftime("%d %B %Y")
            )
        elif "tomorrow" in date_time_str:
            date_time_str = date_time_str.replace(
                "tomorrow", (datetime.now() + timedelta(days=1)).strftime("%d %B %Y")
            )
        for fmt in ("%d %B %Y %H:%M", "%d %m %Y %H:%M", "%d %B %H:%M"):
            try:
                dt = datetime.strptime(date_time_str, fmt)
                return dt.timestamp()
            except ValueError:
                pass
    return None
