import datetime
import logging
import logging.handlers

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    "log.txt", maxBytes=1000000, backupCount=5
)
logger.addHandler(handler)


def thetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log(user, str, save=True):
    str = f"[{thetime()}] [{user.name}] {str}"
    print(str)
    if not save:
        return
    logger.info(str)


def alert(user, str, save=True):
    str = f"[{thetime()}] [{user.name}] {str}"
    print(str)
    if not save:
        return
    logger.warning(str)
