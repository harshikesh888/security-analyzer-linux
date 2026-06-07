import psutil

# Common ports database
KNOWN_PORTS = {
    22: {
        "service": "SSH",
        "safe": True,
        "description": "Secure remote shell service."
    },
    53: {
        "service": "DNS",
        "safe": True,
        "description": "Domain Name System server."
    },
    80: {
        "service": "HTTP",
        "safe": True,
        "description": "Web server."
    },
    443: {
        "service": "HTTPS",
        "safe": True,
        "description": "Secure web server."
    },
    631: {
        "service": "CUPS / IPP",
        "safe": True,
        "description": "Linux printing service."
    },
    3306: {
        "service": "MySQL",
        "safe": True,
        "description": "MySQL database server."
    },
    5432: {
        "service": "PostgreSQL",
        "safe": True,
        "description": "PostgreSQL database server."
    },
    6379: {
        "service": "Redis",
        "safe": True,
        "description": "Redis in-memory database."
    },
    11434: {
        "service": "Ollama API",
        "safe": True,
        "description": "Local Ollama AI API."
    },
    63342: {
        "service": "JetBrains Built-in Server",
        "safe": True,
        "description": "PyCharm/IntelliJ local development server."
    }
}


def get_listening_ports():
    results = []

    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_LISTEN:
            continue

        port = conn.laddr.port
        address = conn.laddr.ip
        pid = conn.pid

        process = "Unknown"
        username = "Unknown"

        if pid:
            try:
                p = psutil.Process(pid)
                process = p.name()
                username = p.username()
            except Exception:
                pass

        port_info = KNOWN_PORTS.get(port)

        # Determine exposure
        if address in ("127.0.0.1", "::1"):
            exposure = "Localhost only"
            exposure_risk = "LOW"
        else:
            exposure = "Network accessible"
            exposure_risk = "MEDIUM"

        if port_info:
            service = port_info["service"]
            description = port_info["description"]

            if exposure == "Localhost only":
                risk = "LOW"
                verdict = "Expected local service."
            else:
                risk = "MEDIUM"
                verdict = "Verify this service should be externally accessible."

        else:
            service = "Unknown"
            description = "Port is not in local knowledge base."

            if exposure == "Localhost only":
                risk = "MEDIUM"
                verdict = "Unknown local service. Verify manually."
            else:
                risk = "HIGH"
                verdict = "Unknown externally accessible service."

        results.append({
            "port": port,
            "address": address,
            "pid": pid,
            "process": process,
            "user": username,
            "service": service,
            "exposure": exposure,
            "risk": risk,
            "description": description,
            "analysis": verdict
        })

    return results