import datetime
import os

from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection


ROUTER_IP = os.getenv('ROUTER_IP')  # e.g. 192.168.0.1
if not ROUTER_IP:
    raise ValueError('ROUTER_IP Environment Variable is required')

ROUTER_USER = os.getenv('ROUTER_USER')
if not ROUTER_USER:
    raise ValueError('ROUTER_USER Environment Variable  is required')

ROUTER_PASS = os.getenv('ROUTER_PASS')
if not ROUTER_PASS:
    raise ValueError('ROUTER_PASS Environment Variable  is required')

def format_uptime(seconds: int) -> str:
    uptime = datetime.timedelta(seconds=seconds)
    days, remainder = divmod(uptime.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

# Connect to router
with Connection(f"http://{ROUTER_USER}:{ROUTER_PASS}@{ROUTER_IP}/") as conn:
    client = Client(conn)

    stats = client.monitoring.traffic_statistics()
    uptime = stats["CurrentConnectTime"]
    print(f"Connected to router with uptime: {format_uptime(int(uptime))}.")

    print("Rebooting!")
    client.device.reboot()
