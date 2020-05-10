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
URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-3h&to=now&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT


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

def mainLoop():
    while True:
        print("Getting rendering")
        getLatestRendering2()
        time.sleep(1)
        
#mainLoop()
fname = "special://temp/" + randomString() + ".png"
print(fname)

getLatestRendering2()
