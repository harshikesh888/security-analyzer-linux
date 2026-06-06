import subprocess

def get_failed_logins():

    logs = subprocess.check_output(
        ["journalctl", "-n", "200", "--no-pager"],
        text=True
    )

    failures = []

    for line in logs.split("\n"):
        if "Failed password" in line:
            failures.append(line)

    return failures
