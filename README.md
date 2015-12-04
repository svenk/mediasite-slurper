# Download videos from the SonicFoundry platform

This repsository contains (a) Python script(s) to download videos (MP4 files) or actually working
out the URL to download specific videos. This can be done without much hazzle as the web based
video plattform highly depends on JavaScript and JSON, and it is easy to trigger the specific
HTTP queries to gather the data needed. Actually, MediaSite is a surprisingly open platform.

## Features

* Extract based on a video playback URL
* Embeddable in a python program or runnable as standalone, works fine with the command line
* Extensible by means of information extraction
* Can display the title, chapters, Video URL
* Can hide as a browser

## Limits and extension proposals

* Did not implement yet any authentification system
* Does not trigger all browser behaviour -- detecting the behaviour is currently easily trackable
* Does not yet download slides (JPGs). However, the algorithm is already described in the script.
* Does not yet cover Silverlight streaming. Currently, only HTML5 video broadcasting is caught.
  Capturing Silverlight would actually require a virtual playback of the video, e.g. with Moonlight
  and Xvfb.

## Usage examples

This code can be run from the command line as

```
python mediasite-download.py --help
```

Invoke with something like

```
python mediasite-download.py --format html --parse "http://your-media.platform.example.com/MediaSite/Play/1b5ea1e55708651e658f0f42198cc5ad?catalog=fa5f9780-9a7f-11e5-8994-feff819cdc9f"
```

Or inspect the data using IPython and running the clases from there.
