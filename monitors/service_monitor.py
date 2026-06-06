import subprocess

def get_services():

    try:
        output = subprocess.check_output(
            [
                "systemctl",
                "list-unit-files",
                "--type=service"
            ],
            text=True
        )

        return output.split("\n")[:30]

    except:
        return []
