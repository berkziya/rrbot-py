import datetime


def thetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log(user, str, save=True):
    str = f"[{thetime()}] [{user.name}] {str}"
    print(str)
    if not save:
        return
    with open("log.txt", "a") as f:
        f.write("[INFO]" + str + "\n")


def alert(user, str, save=True):
    str = f"[{thetime()}] [{user.name}] {str}"
    print(str)
    if not save:
        return
    with open("log.txt", "a") as f:
        f.write("[ALERT] " + str + "\n")
