import sys
from typing import NoReturn
from numpy import NaN
import requests
from libs.cloudflare import CloudFlare
from libs.logging_setup import logger

import asyncio
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

dIntervalTimeout = config.getint("General", "IntervalTimeout")
email = config.get("CloudFlareAPI", "email").strip('",')
token = config.get("CloudFlareAPI", 'password').strip('",')
fqdn = config.get("CloudFlareAPI", "FQDN").strip('",')

CloudflareAPI = CloudFlare(
    email=email,
    password=token
)

def FetchPublicAddress() -> str:
    response = requests.get("https://api.ipify.org?format=json")
    if not response.ok:
        logger.exception(ConnectionError(f"Cannot response to fetch public ip. ({response.status_code}: {response.text})"))
        exit(-1)

    ip_address = response.json()["ip"]

    return ip_address

async def IntervalUpdate(interval: int) -> NoReturn:
    while True:
        # Fetch and update IP address
        address = FetchPublicAddress()
        if address:
            CloudflareAPI.A(fqdn, address)

        await asyncio.sleep(interval)

if __name__ == '__main__':
    print(f"Interval timeout specifies the time between each loop check and update.\n- Note. In minutes only... (Default is {dIntervalTimeout} minutes)")
    interval = int(input("IntervalTimeout: ") or dIntervalTimeout) * 60

    logger.info(f"Initializer Interval Timeout to {interval//60} minutes.")

    # Run the main coroutine
    try:
        asyncio.run(IntervalUpdate(interval=interval))
    except KeyboardInterrupt:
        logger.info("\nSaving log...")
        logger.info("KeyboardInterrupted. Exiting...")
        sys.exit(0)