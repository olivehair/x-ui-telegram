import json
import os
import requests
import re
from dotenv import load_dotenv
from telegram.ext import ContextTypes

load_dotenv()
URLS_JSON = open('urls.json')
SERVER_URLS = json.load(URLS_JSON)


async def update_clients_info(context: ContextTypes.DEFAULT_TYPE):
    print("clients info update has started")
    uuid_map = dict()

    for URL in SERVER_URLS:
        url_groups = re.match(r"https://(.*)/(.*)", URL).groups()
        domain_name = url_groups[0]

        headers = {
            "Accept": "application/json text/plain */*",
            "Accept-Language": "en-USen;q=0.5",
            "Accept-Encoding": "gzip deflate br",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Content-Length": "0",
            "Origin": domain_name,
            "Connection": "keep-alive",
            "Referer": URL + "/xui/inbounds",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
        }

        data = {
            "username": os.environ.get("PANEL_USERNAME"),
            "password": os.environ.get("PANEL_PASSWORD"),
        }
        s = requests.Session()
        s.post(URL + "/login", headers=headers, data=data)

        r2 = s.post(URL + "/xui/inbound/list", headers=headers)
        response = r2.json()

        for inbound in response['obj']:
            client_stats = inbound['clientStats']
            settings = json.loads(inbound['settings'])
            clients = settings['clients']
            for client in clients:
                client_id = client["id"]
                client_email = client['email']
                for stat in client_stats:
                    if stat['email'] == client_email:
                        info = {
                            "enable": stat['enable'],
                            "uuid": client_id,
                            "email": client_email,
                            "up": stat['up'],
                            "down": stat['down'],
                            "total": stat['total'],
                            "expiryTime": stat['expiryTime'],
                        }
                        uuid_map.update({client_id: info})

    json_object = json.dumps(uuid_map, indent=4)
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)
    print("clients info update has finished")
