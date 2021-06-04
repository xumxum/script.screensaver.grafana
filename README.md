# Kodi Grafana screensaver
Kodi screensaver that displays Grafana rendered dashboards

## Requirements
You need a rendering service that renders the grafana dashboards and returns it as an image.  
There are more options for this:

#### grafana-image-renderer plugin

Grafana installed with grafana-image-renderer:
https://github.com/grafana/grafana-image-renderer

#### rendertrone
A Headless Chrome rendering solution  
https://github.com/GoogleChrome/rendertron

Recommend to install rendertron , as it is much faster and less cpu intensive then the grafana-image-render plugin , which performs poorly on multiple renderings. Plus rendertron can render any website/dashboards you might have, not just from grafana and all these will be displayed in the kodi by this screensaver.
