#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib
import time
import random
import string

from pprint import pprint

RENDER_WIDTH = '1920'
RENDER_HEIGHT = '1080'

TMP_IMG="/tmp/grafana.png"
URL_SIZE_SUFFIX = '&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT


def getLatestRendering2():
    try:
        image_on_web = urllib.urlopen(URL)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            downloaded_image = file(TMP_IMG, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return False
    except:
        return False
    return True


def randomString(stringLength=16):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def readUrls():
    try:
        with open('/home/zsolt/.kodi/addons/script.screensaver.grafana/urls.txt', 'r') as f:
            return f.read().splitlines();
    except:
        return []

def mainLoop():
    while True:
        print("Getting rendering")
        getLatestRendering2()
        time.sleep(1)

#mainLoop()
urls = readUrls()
pprint(urls)

if urls:
    for i,u in enumerate(urls):
        urls[i] = u + URL_SIZE_SUFFIX


pprint(urls)
print("urls 0: ")
print(urls[0])
