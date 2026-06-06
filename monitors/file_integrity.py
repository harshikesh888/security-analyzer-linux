import hashlib
from config import WATCH_FILES

def sha256(path):

    try:
        with open(path, "rb") as f:
            return hashlib.sha256(
                f.read()
            ).hexdigest()
    except:
        return "ERROR"

def check_files():

    result = {}

    for f in WATCH_FILES:
        result[f] = sha256(f)

    return result
