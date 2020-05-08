#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib
import time

from pprint import pprint

URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-3h&to=now&width=1920&height=1080'
TMP_IMG = "grafana.png"

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

    
    

def mainLoop():
    while True:
        print("Getting rendering")
        getLatestRendering2()
        time.sleep(1)
        
mainLoop()
