# This is a really advanced files
# Python beginners should not look at this file
# This is so complex, even microsoft doesn't know what it does or how it works
# (I'm being sarcastic if that wasn't getting the point across)
from datetime import datetime
logfile = open("./log.txt", "w+")


def log(content: str):
    new = ""
    for line in content.splitlines():
        new += f"[{datetime.now().strftime('%X %x')}] {line}\n"
    logfile.write(
        new
    )


log("Logger started.")
