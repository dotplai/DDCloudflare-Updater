import requests

from libs.logging_setup import logger

class CloudFlare:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def __GetZone__(self, domain: str) -> str:
        url = "https://api.cloudflare.com/client/v4/zones"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": self.email,
            "Authorization": f"Bearer {self.password}"
        }

        response = requests.get(url, headers=headers, params={ "name": domain })
        data = response.json()

        if not response.ok:
            logger.exception(ConnectionError(f"{response.status_code}: {response.text}"))
            exit(-1)

        if data['success'] and data['result']:
            return data['result'][0]['id']
        else:
            logger.exception(ConnectionRefusedError("Domain not found or API call unsuccessful."))
            exit(-1)

    def __GetRecord__(self, zone: str, record_name: str) -> str:
        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": self.email,
            "Authorization": f"Bearer {self.password}"
        }

        response = requests.get(url, headers=headers, params={ "name": record_name })
        data = response.json()

        if not response.ok:
            logger.exception(ConnectionError(f"{response.status_code}: {response.text}.\n{data['errors']}"))
            exit(-1)

        if data['success'] and data['result']:
            return data['result'][0]['id']
        else:
            logger.exception(ConnectionRefusedError("DNSRecords not found or API call unsuccessful."))
            exit(-1)

    def getDNSRecords(self, zone: str, filter: object = None) -> dict:
        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": self.email,
            "Authorization": f"Bearer {self.password}",
        }

        response = requests.get(url, headers=headers, params=filter)
        response.raise_for_status()
        data = response.json()

        if not response.ok:
            logger.exception(ConnectionError(f"{response.status_code}: {response.text}.\n{data['errors']}"))
            exit(-1)
        
        return data['result']

    def A(self, domain: str, content: str, ttl: int = None, proxied: bool = None, comment: str = None) -> None:
        zone = self.__GetZone__(domain)
        dns_record = self.__GetRecord__(zone, domain)
        oldone = self.getDNSRecords(zone, {'name': domain})
        if oldone is None or oldone == []: return logger.error(KeyError(f"No domain name '{domain}' on your DNSRecords... please create new one before."))

        if content == oldone[0]['content']:
            return logger.info(f"No changes needed for \"{domain}\".")

        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{dns_record}"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": self.email,
            "Authorization": f"Bearer {self.password}",
        }
        data = {
            "type": "A",
            "name": domain,
            "content": content,
            "ttl": ttl if ttl is not None else oldone[0]['ttl'],
            "proxied": proxied if proxied is not None else oldone[0]['proxied'],

            "comment": f"{comment if comment is not None else oldone[0]['comment']}"
        }

        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        if not response.ok:
            logger.exception(ConnectionError(f"{response.status_code}: {response.text}\n{result['errors']}"))

        if not result["success"]:
            return logger.error(ConnectionRefusedError(f"Con't updating content of \"{domain}\" to \"{content}\".\n{result['errors']}"))

        logger.info(f"Successfully updated content to {content}.")

