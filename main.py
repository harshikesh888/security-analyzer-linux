import json

from monitors.auth_monitor import get_failed_logins
from monitors.firewall_monitor import get_firewall_hash
from monitors.process_monitor import get_processes
from monitors.network_monitor import get_listening_ports
from monitors.file_integrity import check_files
from monitors.service_monitor import get_services
from monitors.user_monitor import get_users
from monitors.cron_monitor import get_cron_jobs
from monitors.system_monitor import get_system_stats

from ai_engine import analyze, describe_backend

# Collect data
report = {
    "system": get_system_stats(),
    "failed_logins": get_failed_logins(),
    "firewall_hash": get_firewall_hash(),
    "processes": get_processes(),
    "listening_ports": get_listening_ports(),
    "critical_files": check_files(),
    "services": get_services(),
    "users": get_users(),
    "cron_jobs": get_cron_jobs()
}

# Print collected information
print("=" * 50)
print("SERVER REPORT")
print("=" * 50)
print(json.dumps(report, indent=4))

# AI Analysis
print("\n" + "=" * 50)
print("AI ANALYSIS")
print("=" * 50)
print(f"Backend: {describe_backend()}\n")

try:
    analysis = analyze(report)
except Exception as exc:
    print(f"[!] AI analysis failed: {exc}")
    raise SystemExit(1)

print(analysis)