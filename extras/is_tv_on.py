#!/usr/bin/python3

from requests import get
import json
#Click on your user Home assistant ,Scroll down to Long-Lived Access Tokens and generate a TOKEN
#They paste it here
TOKEN='###___PASTE_HOME_ASSISTANT_LONG_TERM_TOKEN_HERE___####'

url = "http://192.168.1.100:8123/api/states/media_player.lg_webos_tv_un74003lb"
headers = {
    "Authorization": "Bearer "+TOKEN,
    "content-type": "application/json",
}

response = get(url, headers=headers)
d=json.loads(response.text)
#print(response.text)
print(d['state'])
