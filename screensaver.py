#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013 Tristan Fischer (sphere@dersphere.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import xbmcaddon
import xbmcgui
import xbmc

#import requests
import urllib
import os
import random
import string

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


CONTROL_BACKGROUND = 1
#CONTROL_ANIMATED_RAINBOW = 2

#maybe put them in settings also?
RENDER_WIDTH = '1920'
RENDER_HEIGHT = '1080'

TMP_PATH = "special://temp/"
#TMP_PATH = "/tmp/"

URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-15m&to=now&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT

#Since grafan stores by default all temporary rendered data for 24h, might be a good idea to lower that time to 1m for example
#[[paths]]
#    temp_data_lifetime=1m


class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    def onInit(self):
        self.exit_monitor = self.ExitMonitor(self.exit)
        self.abort_requested = False
        self.tempPicture = ""
        self.tempPathOs = xbmc.translatePath(TMP_PATH)
        self.image1 = self.getControl(CONTROL_BACKGROUND)

        self.handle_settings()
        self.mainLoop()

    def handle_settings(self):
        self.interval = addon.getSetting('refresh_interval')

    def exit(self):
        self.abort_requested = True
        self.exit_monitor = None
        self.log('exit signalled')

        
    #doesnt work in python 2 on ubuntu?..
    def getLatestRendering(self):
        page = requests.get(URL)
        content = page.content
    
        with open(TMP_IMG, 'wb') as fd:
            fd.write(content)
            fd.close()

    #python 2 compatible..
    def getLatestRendering2(self):
        try:
            image_on_web = urllib.urlopen(URL)
            if image_on_web.headers.maintype == 'image':
                buf = image_on_web.read()
                downloaded_image = file(self.tempPicture, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
                image_on_web.close()
            else:
                return False
        except:
            return False
        return True


    def randomString(self,stringLength=16):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(stringLength))   


    def mainLoop(self):
        self.log('Grafana mainloop')
        
        while (not self.abort_requested):
            #setting same image will not refresh kodi strangely, didnt find a way to trigger reload , so we just generate new fname every time and delete
            self.tempPicture = self.tempPathOs + self.randomString() + ".png"
            self.log( self.tempPicture)

            self.getLatestRendering2()
            self.image1.setImage(self.tempPicture,False)
            xbmc.sleep(1000)
            
            os.remove(self.tempPicture)
        
        self.log('exited mainLoop')
        self.close()
                    
        

    def log(self, msg):
        xbmc.log(u'Grafana Screensaver: %s' % msg)


if __name__ == '__main__':
    screensaver = Screensaver(
        'script-Grafana-main.xml',
        addon_path,
        'default',
    )
    screensaver.doModal()
    del screensaver
    sys.modules.clear()
