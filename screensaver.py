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

import urllib.request, urllib.parse, urllib.error
import os
import random
import string
import multiprocessing
from time import *
import subprocess

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

#enable for grafana renderer..
URL_SIZE_SUFFIX = '&width=' + RENDER_WIDTH + '&height=' + RENDER_HEIGHT
#URL_SIZE_SUFFIX = ''

#Since grafan stores by default all temporary rendered data for 24h, might be a good idea to lower that time to 1m for example
#[[paths]]
#    temp_data_lifetime=1m

def is_tv_on():
    TV_ON_EXE='/work/zee/tools/is_tv_on/is_tv_on.py'
    #if no exe to say tv is on..assume it's ON
    if not os.path.exists(TV_ON_EXE):
        return True
    status=subprocess.check_output([TV_ON_EXE]).strip()
    if status == 'ok':
        return True
    return False

# def getLatestRendering2(url, tempPicture):
#     try:
#         if not is_tv_on():
#             return False
#
#         image_on_web = urllib.request.urlopen(url)
#         if image_on_web.headers.maintype == 'image':
#             buf = image_on_web.read()
#             downloaded_image = file(tempPicture, "wb")
#             downloaded_image.write(buf)
#             downloaded_image.close()
#             image_on_web.close()
#         else:
#             return False
#     except:
#         return False
#     return True


def download_image(url, outfile):
    urllib.request.urlretrieve(url,outfile)
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
                urlLines = f.read().splitlines()

                #add width and height , maybe should check first
                for i,u in enumerate(urlLines):
                    if not u.startswith('#'):
                        rez.append(u)
                        self.log('loaded url: {}'.format(rez[-1]))

                self.urls = rez


        except Exception as e:
            msg = 'Could not read url file: {}, exception: {}'.format( urlsFileName, e)
            self.log(msg)
            xbmc.executebuiltin("Notification('Grafan Screensaver','%s')" % msg)
            return []

    def exit(self):
        self.abort_requested = True
        self.exit_monitor = None
        self.log('exit signalled')



    def randomString(self,stringLength=16):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(stringLength))


    #wait min timeout or unti process finished running
    def sleepUntilNextSlide(self):
        #small intervals so it will exit quickly when needed
        #except when rendering
        start_time = time()

        while not self.abort_requested:
            xbmc.sleep(100)

            #if rendering done, set the image asap
            if not self.process.is_alive():
                if os.path.exists(self.tempPicture):
                    self.image1.setImage(self.tempPicture,False)
                    #give some time to set it..otherwise we delete it immediatly when we return
                    #and kodi doesnt have time to set it
                    #maybe shold have a queue of files and delete older ones...
                    xbmc.sleep(100)
                self.process.join()

            #wait done if time expered & rendering done
            if (time() - start_time >= self.interval) and ( not self.process.is_alive() ):
                #time passed and renering process process finished running
                break


    def sleepUntilNextSlide2(self):
        #small intervals so it will exit quickly when needed
        #except when rendering
        start_time = time()

        while not self.abort_requested:
            xbmc.sleep(100)

            #wait done if time expered & rendering done
            if time() - start_time >= self.interval:
                #time passed
                break

    def mainLoop(self):
        self.log('Grafana mainloop')
        self.indexUrl = 0
        self.previoustempPicture = None

        while (not self.abort_requested):
            # #setting same image will not refresh kodi strangely, didnt find a way to trigger reload , so we just generate new fname every time and delete
            # self.tempPicture = self.randomString() + ".png"
            # #kodi accepts only special:// files while write and remote need absolute path..
            # #kodi_fname = TMP_PATH + self.tempPicture
            # self.tempPicture = self.tempPathOs + self.tempPicture
            #
            # self.log( self.tempPicture)

            #xbmc.sleep(1000)
            #render_ok = self.getLatestRendering()

            # if self.urls:
            #     url = self.urls[self.indexUrl]
            #     self.process = multiprocessing.Process(target=getLatestRendering2, args=(url, self.tempPicture,))
            #     self.process.start()
            #
            #
            # self.sleepUntilNextSlide()
            #
            # try:
            #     os.remove(self.tempPicture)
            # except:
            #     pass
            #
            # #go to next url
            # if self.urls:
            #     self.indexUrl = (self.indexUrl + 1) % len(self.urls)
            #     #resync urls text file every cycle
            #     if self.indexUrl == 0:
            #         self.readUrls()



            if self.urls:
                url = self.urls[self.indexUrl]

                #setting same image will not refresh kodi strangely, didnt find a way to trigger reload , so we just generate new fname every time and delete
                self.tempPicture = self.tempPathOs + self.randomString() + ".png"
                self.log( self.tempPicture)

                render_ok = download_image(url, self.tempPicture)
                self.log(f'Render returned: {render_ok}')

                if os.path.exists(self.tempPicture):
                    self.log(f'Setting image: {self.tempPicture}')
                    self.image1.setImage(self.tempPicture,False)

            #remove previous tmpPicture
            try:
                os.remove(self.previoustempPicture)
            except:
                pass

            self.sleepUntilNextSlide2()

            self.previoustempPicture = self.tempPicture
            #go to next url
            if self.urls:
                self.indexUrl = (self.indexUrl + 1) % len(self.urls)
                #resync urls text file every cycle
                if self.indexUrl == 0:
                    self.readUrls()


        self.log('exited mainLoop')

        try:
            os.remove(self.previoustempPicture)
        except:
            pass
        # if self.process.is_alive():
        #     self.process.terminate()

        self.close()



    def log(self, msg):
        xbmc.log('Grafana Screensaver: %s' % msg)


if __name__ == '__main__':
    screensaver = Screensaver(
        'script-Grafana-main.xml',
        addon_path,
        'default',
    )
    screensaver.doModal()
    del screensaver
    #sys.modules.clear()
