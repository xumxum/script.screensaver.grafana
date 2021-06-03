#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib
import re
from pprint import pprint
import sys

URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-3h&to=now&width=1920&height=1080'
URL_RENDERTRON='http://192.168.1.11:3001/screenshot/http://nuc:3000/d/VLVPGnRMz/zeenet2?orgId=1&refresh=5s'
TMP_IMG="/tmp/grafana.png"

def getLatestRendering():
    page = requests.get(URL)
    content = page.content

    with open("/tmp/grafana.png", 'wb') as fd:
        fd.write(content)
        fd.close()


def getLatestRendering2(url, tempPicture):
    try:

        image_on_web = urllib.urlopen(url)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            downloaded_image = file(tempPicture, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return False
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        return False
    return True

def mainLoop():
    while True:
        print("Getting rendering")
        getLatestRendering2(URL_RENDERTRON, TMP_IMG)

mainLoop()
