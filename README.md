# Kodi Grafana screensaver
Kodi screensaver that displays Grafana rendered dashboards

## Requirements

#### Grafana & grafana-image-renderer plugin
You need to have Grafana installed and a rendering service that renders the Grafana dashboards and returns it as an image. Recommend to use the default grafana rendering service, which can be installed as a plugin in Grafana

> https://github.com/grafana/grafana-image-renderer

#### Kodi
Kodi 19 is the latest kodi supported, though kodi 18 will probably work as well if you use the kodi18 branch from the source code.

## Installation
To install follow the steps bellow:
- Go to: https://github.com/xumxum/script.screensaver.grafana

- Click Code -> Download zip

- In Kodi, go to Add Ons and install the addon from zip file you just downloaded

- Change grafana.ini `temp_data_lifetime = 1m`. By default Grafana will store the rendered images for 24h, so it's good practice to reduce it to just one minute.    
Restart grafana service, so the config option is enabled. `systemctl restart grafana.service`

- Create urls file that will be rendered. See URL File section   
Make sure that each url from the urls file is working by trying it inside a browser first. The link should return an image file of the dashboard rendered.

- In kodi, go to System -> Interface -> Screensaver and configure Grafana as your default screensaver. Also change wait time, the time after the screensaver will start, if nothing is pressed in kodi. I personally have 1 minute only, so the Grafana screensaver will start asap.




#### URL File
Grafana will read the urls file configured in settings and each url line will be downloaded periodically and set as a screensaver background.   
The render url is the same as the dashboard url, with the `/render/` inserted before the `/d/` part of the url.   
For example if the local link to a grafana dashboard is :
`http://192.168.1.100:3000/d/q4jAnx6Zk/dashboard1?orgId=1&from=now-1h&to=now`   
The grafana image rendered link will be
`http://192.168.1.100:3000/render/d/q4jAnx6Zk/dashboard1?orgId=1&refresh=5s&from=now-3h&to=now&kiosk`

Notes:
- grafana-image-rendered can hang if some parameters are missing...I found out that adding `refresh=5s`to the url helps.
- you can specify `width=` and `height=` in the url directly, if not the width and height from the Screensaver settings will be appended to the url before rendering
- `kiosk` is also recommended to be added to the url, as it will remove the left manu part of the dashboard

See sample url file in `./extras/urls.txt`
#### is_tv_on
To save power & fan noise, an extra feature of this plugin is the external script is_tv_on. Before rendering is started, this script is called and if the script will return the string `on` in the output, the rendering will continue, otherwise we consider the tv is off, and there is no point in rendering at the moment.

If there is no is_tv_on binary configured, feature is considered disabled and it will always start rendering. If the binary is found, it is executed and only if the script returns `on`, rendering will continue.

An example implementation is by interogating home assistant of the state of a media player , See sample file in `./extras/is_tv_on.py`

You can create your own custom script and point the binary in Grafana screensaver settings. One example could be that the script will consider the tv to be on between 9am and 6pm, thus saving power outside of working hours.

## Notes
- Do not set the interval to low as the grafana-image-rendering is processor intensive. It will start a chromium browser in the background and load the grafana dashboard, then return it as an image. I am using it on a strong Intel NUC i5 hardware and it can take the load, if you have a raspberry or lower spec hardware, check the cpu

- grafana-image-rendered is still experimental and processor heavy, can also have bugs in older versions.
