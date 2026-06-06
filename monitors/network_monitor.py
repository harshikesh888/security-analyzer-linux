import psutil

def get_listening_ports():

    ports = []

    for c in psutil.net_connections(
        kind="inet"
    ):
        if c.status == "LISTEN":
            ports.append({
                "port": c.laddr.port,
                "pid": c.pid
            })

    return ports
