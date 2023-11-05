

LOG_FILE_PATH = "chat_app/chat_app.log"


def clear_log():
    with open(LOG_FILE_PATH, "w") as f:
        f.write("")


def log(msg):
    with open(LOG_FILE_PATH, "a") as f:
        f.write(msg + "\n")
