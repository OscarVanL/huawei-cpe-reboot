import datetime
import logging
import os
import time

import requests
import speedtest
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection

logging.basicConfig(level=logging.INFO)


ROUTER_IP = os.getenv('ROUTER_IP')  # e.g. 192.168.0.1
if not ROUTER_IP:
    raise ValueError('ROUTER_IP Environment Variable is required')

ROUTER_USER = os.getenv('ROUTER_USER')
if not ROUTER_USER:
    raise ValueError('ROUTER_USER Environment Variable  is required')

ROUTER_PASS = os.getenv('ROUTER_PASS')
if not ROUTER_PASS:
    raise ValueError('ROUTER_PASS Environment Variable  is required')

def measure_speed() -> tuple[float, float, float]:
    st = speedtest.Speedtest()
    st.download()
    st.upload()
    st.get_best_server()

    download_speed = st.results.download / 1_000_000  # Convert to Mbps
    upload_speed = st.results.upload / 1_000_000  # Convert to Mbps
    ping = st.results.ping

    return download_speed, upload_speed, ping

def format_uptime(seconds: int) -> str:
    uptime = datetime.timedelta(seconds=seconds)
    days, remainder = divmod(uptime.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

def wait_for_reboot(max_wait: int = 300):
    start_time = time.time()
    while True:
        try:
            with Connection(f"http://{ROUTER_USER}:{ROUTER_PASS}@{ROUTER_IP}/", timeout=5) as conn:
                client = Client(conn)
                stats = client.monitoring.traffic_statistics()
                uptime = stats["CurrentConnectTime"]
                # Router has been up for less than 60 seconds, so we can assume it has rebooted
                if 0 < int(uptime) < 60:
                    logging.info(f"Got uptime of {format_uptime(int(uptime))}, assuming router has rebooted.")
                    return
        except requests.exceptions.ConnectionError:
            pass

        if time.time() - start_time > max_wait:
            raise TimeoutError(f"Router did not come back online within {max_wait}. Giving up.")

        time.sleep(5)

def main():
    # Connect to router
    with Connection(f"http://{ROUTER_USER}:{ROUTER_PASS}@{ROUTER_IP}/") as conn:
        client = Client(conn)

        logging.info(f"Connecting to router...")

        stats = client.monitoring.traffic_statistics()
        uptime = stats["CurrentConnectTime"]
        logging.info(f"Connected to router with uptime: {format_uptime(int(uptime))}.")

        logging.info(f"Measuring speed (pre-reboot)...")
        download_speed, upload_speed, ping = measure_speed()
        logging.info(f"Results: Download Speed: {download_speed:.2f} Mbps, Upload Speed: {upload_speed:.2f} Mbps, Ping: {ping:.2f} ms")

        logging.info("Rebooting!")
        client.device.reboot()

    logging.info("Waiting for router to reboot...")
    try:
        wait_for_reboot()
    except TimeoutError:
        logging.exception("Router did not come back online. Exiting.")
        return

    logging.info(f"Measuring speed (post-reboot)...")
    download_speed, upload_speed, ping = measure_speed()
    logging.info(
        f"Results: Download Speed: {download_speed:.2f} Mbps, Upload Speed: {upload_speed:.2f} Mbps, Ping: {ping:.2f} ms")

if __name__ == "__main__":
    main()


