import subprocess
import hashlib

def get_firewall_hash():

    try:
        rules = subprocess.check_output(
            ["sudo", "nft", "list", "ruleset"],
            text=True
        )

        return hashlib.sha256(
            rules.encode()
        ).hexdigest()

    except:
        return "Firewall unavailable"
