import psutil

def get_processes():

    procs = []

    for p in psutil.process_iter(
        ["pid", "name", "username"]
    ):
        try:
            procs.append(p.info)
        except:
            pass

    return procs[:20]
