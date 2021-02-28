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

import urllib
import os
import random
import string
import multiprocessing

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


CONTROL_BACKGROUND = 1


#maybe put them in settings also?
RENDER_WIDTH = '1920'
RENDER_HEIGHT = '1080'

#doesnt work in this format but it should..
#TMP_PATH = "special://temp/"
TMP_PATH = "/tmp/"

URL_SIZE_SUFFIX = '&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT

#Since grafan stores by default all temporary rendered data for 24h, might be a good idea to lower that time to 1m for example
#[[paths]]
#    temp_data_lifetime=1m

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
    except:
        return False
    return True


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
        self.indexUrl = 0
        #self.tempPathOs = xbmc.translatePath(TMP_PATH)
        self.tempPathOs = TMP_PATH
        self.image1 = self.getControl(CONTROL_BACKGROUND)

        self.read_settings()
        self.readUrls()

        if self.urls:
            for i,u in enumerate(self.urls):
                self.log(u)
                self.urls[i] = u + URL_SIZE_SUFFIX
                #self.log(self.urls[i])

        self.mainLoop()


    def read_settings(self):
        self.interval = int(addon.getSetting('refresh_interval'))
        self.urls_file = addon.getSetting('urls_file')
        #ADDON.getSettingString('path')
        #ADDON.getSettingInt('time')

    def readUrls(self):
        try:
            rez = []
            urlsFileName = self.urls_file
            self.log(urlsFileName)
            with open(urlsFileName, 'r') as f:
                self.log("Opened urls file")
                rez = f.read().splitlines()

                #add width and height , maybe should check first
                for i,u in enumerate(rez):
                    rez[i] = u + URL_SIZE_SUFFIX
                    self.log(u'added with and height to url: {}'.format(rez[i]))

                self.urls = rez


        except Exception as e:
            msg = u'Could not read url file: {}, exception: {}'.format( urlsFileName, e)
            self.log(msg)
            xbmc.executebuiltin(u"Notification('Grafan Screensaver','%s')" % msg)
            return []

    def exit(self):
        self.abort_requested = True
        self.exit_monitor = None
        self.log('exit signalled')



    def randomString(self,stringLength=16):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(stringLength))

    def sleepUntilNextSlide(self):
        #small intervals so it will exit quickly when needed
        #except when rendering
        sleepCycles = self.interval * 10;
        while ((sleepCycles > 0) and (not self.abort_requested)):
            xbmc.sleep(100)
            sleepCycles = sleepCycles - 1
            if not self.process.is_alive():
                if os.path.exists(self.tempPicture):
                    self.image1.setImage(self.tempPicture,False)
                self.process.join()

            #self.log(sleepCycles)


    def mainLoop(self):
        self.log('Grafana mainloop')
        self.indexUrl = 0

        while (not self.abort_requested):
            #setting same image will not refresh kodi strangely, didnt find a way to trigger reload , so we just generate new fname every time and delete
            self.tempPicture = self.randomString() + ".png"
            #kodi accepts only special:// files while write and remote need absolute path..
            #kodi_fname = TMP_PATH + self.tempPicture
            self.tempPicture = self.tempPathOs + self.tempPicture

            #self.log( self.tempPicture)

            #render_ok = self.getLatestRendering()

            if self.urls:
                url = self.urls[self.indexUrl]
                self.process = multiprocessing.Process(target=getLatestRendering2, args=(url, self.tempPicture,))
                self.process.start()


            self.sleepUntilNextSlide()

            try:
                os.remove(self.tempPicture)
            except:
                pass

            #go to next url
            if self.urls:
                self.indexUrl = (self.indexUrl + 1) % len(self.urls)
                #resync urls text file every cycle
                if self.indexUrl == 0:
                    self.readUrls()

        self.log('exited mainLoop')

        if self.process.is_alive():
            self.process.terminate()

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
