#!/usr/bin/python3

import xbmcaddon
import xbmcgui
import xbmc

import os
import random
import string
from time import *

import socket
from concurrent import futures
from http.client import HTTPConnection
import subprocess


addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


CONTROL_BACKGROUND = 1

DEBUG_LOGS = False

#doesnt work in this format but it should..
#TMP_PATH = "special://temp/"
TMP_PATH = "/tmp/"


#Since grafan stores by default all temporary rendered data for 24h, might be a good idea to lower that time to 1m for example
#[[paths]]
#    temp_data_lifetime=1m


#download of grafana rendered image that can be called as a future
def download_image_interruptible(con, url, outfile):
    #xbmc.log(f'Grafana Screensaver: download_image_interruptable {url}->{outfile}')
    con.request('GET', url)
    response = con.getresponse()
    payload = response.read()
    #save payload to file
    with open( outfile, 'wb') as f:
        f.write( payload )
        f.close()
    #save data to file
    return response


class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    def onInit(self):
        self.exit_monitor = self.ExitMonitor(self.exit)
        self.abort_requested = False
        self.tempPictures=[]
        self.indexUrl = 0
        #self.tempPathOs = xbmc.translatePath(TMP_PATH)
        self.tempPathOs = TMP_PATH
        self.image1 = self.getControl(CONTROL_BACKGROUND)
        self.executor = futures.ThreadPoolExecutor()
        self.future = None

        self.read_settings()
        self.readUrls()

        if self.urls:
            for i,u in enumerate(self.urls):
                self.log(u)
                #if no widht and height in the url, add it,we must have otherwise is some lowress default
                if '&width=' not in u:
                    self.urls[i] = u + self.url_size_suffix
                else:
                    self.urls[i] = u
                #self.log(self.urls[i])

        self.mainloop()


    def read_settings(self):
        self.interval = int(addon.getSetting('refresh_interval'))
        self.urls_file = addon.getSetting('urls_file')
        self.tv_on_exe = addon.getSetting('tv_on_exe')
        render_width = int(addon.getSetting('render_width'))
        render_height = int(addon.getSetting('render_height'))
        self.url_size_suffix = '&width=' + str(render_width) + '&height=' + str(render_height)

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

    #Call external script(if it exists) to check if the tv is on or not
    def is_tv_on(self):
        #if no exe to say tv is on..assume it's ON
        if not os.path.exists(self.tv_on_exe):
            return True
        status=subprocess.check_output([self.tv_on_exe]).decode('utf-8').strip()
        if status == 'on':
            return True
        return False

    def randomString(self,stringLength=16):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(stringLength))

    #substract the domain and port from an URL..
    def getHostPort(self, URL):
        s = URL.find('//')
        if s ==-1:
            s = 0
        else:
            s=s+2
        e = URL.find('/', s)
        if s !=-1 and e!=-1:
            return URL[s:e]
        else:
            return ''


    def start_rendering(self):
        url = self.urls[self.indexUrl]

        #setting same image will not refresh kodi strangely, didnt find a way to trigger reload , so we just generate new fname every time and delete
        tempPicture = self.tempPathOs + self.randomString() + ".png"
        self.log(f'start rendering {url} -> {tempPicture}')
        self.tempPictures.append(tempPicture)

        host_and_port = self.getHostPort(url)
        self.con = HTTPConnection(host_and_port)
        self.future = self.executor.submit(download_image_interruptible, self.con, url, tempPicture)

        #go to next url
        if self.urls:
            self.indexUrl = (self.indexUrl + 1) % len(self.urls)
            #resync urls text file every cycle
            if self.indexUrl == 0:
                self.readUrls()


    #Delete the old temp files, should be one the previous one
    def delete_old_temp_pictures(self, all=False):
        if not self.tempPictures:
            return
        #how many to delete
        count = len(self.tempPictures) - 1
        if all:
            count = count + 1

        for _ in range(count):
            tempPicture = self.tempPictures.pop(0)
            if os.path.exists(tempPicture):
                try:
                    os.remove(tempPicture)
                except:
                    pass

    def mainloop(self):
        self.log('Grafana mainloop')
        self.indexUrl = 0
        state = 'ST_WAITING' #ST_RENDERING
        start_time = 0 # force it to go directly to render

        while (not self.abort_requested):
            #self.log(f'state = {state} start_time: {start_time} time: {time()} interval: {self.interval}')
            if state == 'ST_WAITING':
                #waiting for a time until we start the grafana dashboard download
                if time() - start_time >= self.interval:
                    #we waited enough, start next download
                    self.log('Wait over, lets see next')
                    if self.is_tv_on():
                        self.start_rendering()
                        state = 'ST_RENDERING'
                    else:
                        self.log('Tv is not on, restart waiting')
                        #tv is not on, wait some more
                        start_time = time()

            elif state == 'ST_RENDERING':
                if self.future.done():
                    self.log(f'Rendering complete of {self.tempPictures[-1]}')
                    if self.future.exception():
                        self.log(f'exception: {self.future.exception()}')
                    if self.future.result().code != 200:
                        self.log(f'http  result code: {self.future.result().code}')
                    #rendering finished, display it if the file exists, means download was ok
                    if os.path.exists(self.tempPictures[-1]):
                        self.log(f'Setting image: {self.tempPictures[-1]}')
                        self.image1.setImage(self.tempPictures[-1],False)
                        self.delete_old_temp_pictures()

                    start_time = time()
                    state = 'ST_WAITING'

            xbmc.sleep(500)

        #exit signalled
        self.log('exited mainLoop cleanup')
        if self.future:
            if self.future.running():
                self.con.sock.shutdown(socket.SHUT_RDWR)
                self.con.sock.close()

        del self.executor

        self.delete_old_temp_pictures(all=True)
        self.close()
        self.log('screensaver finished!!')



    def log(self, msg):
        if DEBUG_LOGS:
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
