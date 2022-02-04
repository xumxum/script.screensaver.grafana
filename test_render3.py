#!/usr/bin/python3

import random
import urllib.request

URL='http://192.168.1.11:3000/render/d/9BS3sPyGk/internet2?orgId=1&refresh=5s&from=now-3h&to=now&width=1920&height=1080&kiosk'
TMP_FILE='/tmp/test.png'

def download_image(url, outfile):
    urllib.request.urlretrieve(url,outfile)

download_image(URL, TMP_FILE)
