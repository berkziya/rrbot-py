import time

import actions
from butler import error


def handle_input(users, commands, input):
    split = input.split(" ")

    if split[1] == "all":
        split[1] = " ".join([user.name for user in users])

    # <attack or def> <user or all> <id or link> <full or hourly (optional)>
    if split[0] in ["attack", "def"]:
        if len(split) == 3:
            split.append(False)
        for user in users:
            if user.name in split[1]:
                return commands[user].append(
                    war_input(user, split[0], split[2], split[3])
                )

    # <factory> <user or all> <id or link> <full or hourly (optional)>
    elif split[0] == "factory":
        if len(split) == 3:
            split.append(False)
        for user in users:
            if user.name in split[1]:
                return commands[user].append(factory_input(user, split[2], split[3]))


def war_input(user, side, link, full):
    try:
        if link.isdigit():
            id = int(link)
        else:
            id = link.split("/")[-1]
        war = actions.wars.get_war_info(user, id)
        if not war:
            print("War not found")
            return False
        if side == "attack":
            side = war[0].id
        elif side == "def":
            side = war[1].id
        if full == "full":
            full = True
        else:
            full = False
        return actions.wars.attack(user, id, side, full)
    except Exception as e:
        return error(user, e, "Error attacking")


def factory_input(user, link, full):
    try:
        if link.isdigit():
            id = int(link)
        else:
            id = link.split("/")[-1]
        if full == "full":
            full = True
        else:
            full = False
        actions.work.assign_factory(user, id)
        time.sleep(2)
        return actions.work.auto_work_factory(user)
    except Exception as e:
        return error(user, e, "Error setting factory")
