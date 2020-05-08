#!/usr/bin/python2
# -*- coding: utf-8 -*-

import requests
import re
from pprint import pprint

URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-3h&to=now&width=1920&height=1080'


def getLatestRendering():
    page = requests.get(URL)
    content = page.content
    
    with open("/tmp/grafana.png", 'wb') as fd:
        fd.write(content)
        fd.close()
        

def mainLoop():
    while True:
        print("Getting rendering")
        getLatestRendering()
        
        
mainLoop()
