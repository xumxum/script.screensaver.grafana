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

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


CONTROL_BACKGROUND = 1
#CONTROL_ANIMATED_RAINBOW = 2

#maybe put them in settings also?
RENDER_WIDTH = '1920'
RENDER_HEIGHT = '1080'

TMP_IMG="/tmp/grafana.png"
URL = 'http://nuc:3000/render/d/q4jAnx6Zk/zeenet?from=now-3h&to=now&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT

#Since grafan stores by default all temporary rendered data for 24h, might be a good idea to lower that time to 1m for example
#[[paths]]
#    temp_data_lifetime=1m

class ExitPlease(Exception):
    pass

class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    def onInit(self):
        self.exit_monitor = self.ExitMonitor(self.exit)
        self.abort_requested = False
        self.handle_settings()
        self.mainLoop()

    def handle_settings(self):
        self.interval = addon.getSetting('refresh_interval')

    def exit(self):
        self.abort_requested = True
        raise ExitPlease
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
                downloaded_image = file(TMP_IMG, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
                image_on_web.close()
            else:
                return False
        except:
            return False
        return True


    def mainLoop(self):
        self.image1 = self.getControl(CONTROL_BACKGROUND)
        #while (not self.exit_monitor.abortRequested()):
        self.log('Grafana mainloop')
        while (not self.abort_requested):
            #print("Getting rendering")
            self.getLatestRendering2()
            self.image1.setImage(TMP_IMG,False)
            xbmc.sleep(1000)
        
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
