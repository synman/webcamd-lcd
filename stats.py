#! /usr/bin/python
# webcam-lcd - A Nifty PIL based driver for displaying webcamd stats with the Adafruit 128x32 PiOLED
#                                                            (https://www.adafruit.com/product/3527)
#
# webcamd is a high performance MJPEG HTTP server and can be found here: https://github.com/synman/webcamd
#
# Written by Shell M. Shrader <shell@shellware.com>
# Original Source / Licence reference:  (https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/blob/main/examples/ssd1306_stats.py)
#
import time
import datetime
import subprocess
import busio
import adafruit_ssd1306

import requests

from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height

# common box height for our graphs
boxH = 8

splashImage = Image.new("1", (width, height))
splashDraw = ImageDraw.Draw(splashImage)

# Draw a black filled box to clear the image.
# splashDraw.rectangle((0, 0, width, height), outline=0, fill=0)

# Load fonts
# font = ImageFont.load_default()
headerFont = ImageFont.truetype('/home/pi/lcdstats/source-code-pro/SourceCodePro-Regular.ttf', 8)
valueFont = ImageFont.truetype('/home/pi/lcdstats/source-code-pro/SourceCodePro-Regular.ttf', 9)
splashFont = ImageFont.truetype('/home/pi/lcdstats/source-code-pro/SourceCodePro-Regular.ttf', 12)

# headerFont = ImageFont.truetype('/home/pi/lcdstats/misc-fixed.ttf', 9)
# valueFont = ImageFont.truetype('/home/pi/lcdstats/misc-fixed.ttf', 10)
# splashFont = ImageFont.truetype('/home/pi/lcdstats/misc-fixed.ttf', 12)

s1 = "webcamd-lcd"
s2 = "------------"
s3 = "By Shellware"

s1w, s1h = splashFont.getsize(s1)
s2w, s2h = valueFont.getsize(s2)
s3w, s3h = valueFont.getsize(s3)

splashDraw.text((width / 2 - s1w / 2, 0),  s1, font=splashFont, fill=255)
splashDraw.text((width / 2 - s2w / 2, s1h + 1),  s2, font=valueFont, fill=255)
splashDraw.text((width / 2 - s3w / 2, s1h + s2h + 2), s3, font=valueFont, fill=255)

disp.image(splashImage)
disp.show()

time.sleep(10)

cmd = "nproc"
cpus = int(subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n", ""))

image = Image.new("1", (height, width))
final = Image.new("1", (width, height))

draw = ImageDraw.Draw(image)
finalDraw = ImageDraw.Draw(final)

cmd = "hostname"
hostname = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n", "")
sessions = -1

url = 'http://localhost:8080/?info'

while True:
    # cmd = "curl 'http://localhost:8080/?info' -s | jq -r '.config.port, .stats.encodeFps, .stats.sessionCount, .stats.avgStreamFps'"
    # webcam = subprocess.check_output(cmd, shell=True).decode("utf-8")
    # stats = webcam.replace("\r", "").split("\n")

    try:
        resp = requests.get(url=url)
        if resp.status_code != 200:
            print("%s: unable to query webcamd: response code = [%d]" % (datetime.datetime.now(), resp.status_code), flush=True)
            time.sleep(5)
            continue

        data = resp.json()

        encodeFps = data["stats"]["encodeFps"]
        streamFps = data["stats"]["avgStreamFps"]
        port = data["config"]["port"]

        # dim the screen if we don't have any active cients
        if sessions != 0 and data["stats"]["sessionCount"] == 0:
            disp.fill(0)
            disp.show()

        sessions = data["stats"]["sessionCount"]

        if sessions == 0:
            time.sleep(10)
            continue

    except Exception as e:
        print("%s: unable to query webcamd: [%s]" % (datetime.datetime.now(), e), flush=True)
        sessions = 0
        disp.fill(0)
        disp.show()
        time.sleep(5)
        continue

    cmd = 'cut -f 1 -d " " /proc/loadavg'
    load = float(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    cpu = load / cpus * 100.
    if cpu > 100: cpu = 100

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, height, width), outline=0, fill=0)


    cH = "CPU"
    cHw, cHh = headerFont.getsize(cH)

    top = 0
    draw.text((height / 2 - cHw / 2, top), cH, font=headerFont, fill=255, spacing=4)

    top = cHh + 1
    draw.rectangle((0, top, 31, top + boxH), outline=255, fill=0)
    draw.rectangle((0, top, int(31 * (cpu / 100)), top + boxH), outline=255, fill=255)

    cV = "%.0f %%" % cpu
    cVw, cVh = valueFont.getsize(cV)

    top = top + boxH + 2
    draw.text((height / 2 - cVw / 2, top), cV, font=valueFont, fill=255)


    cH = "ENCODE"
    cHw, cHh = headerFont.getsize(cH)

    top = top + cVh + 6
    draw.text((height / 2 - cHw / 2, top), cH, font=headerFont, fill=255, spacing=4)

    top = top + cHh + 1
    draw.rectangle((0, top, 31, top + boxH), outline=255, fill=0)
    draw.rectangle((0, top, int(31 * (encodeFps / 30)), top + boxH), outline=255, fill=255)

    cV = "%.0f FPS" % encodeFps
    cVw, cVh = valueFont.getsize(cV)

    top = top + boxH + 2
    draw.text((height / 2 - cVw / 2, top), cV, font=valueFont, fill=255)


    cH = "STREAM"
    cHw, cHh = headerFont.getsize(cH)

    top = top + cVh + 6
    draw.text((height / 2 - cHw / 2, top), cH, font=headerFont, fill=255, spacing=4)

    top = top + cHh + 1
    draw.rectangle((0, top, 31, top + boxH), outline=255, fill=0)
    draw.rectangle((0, top, int(31 * (streamFps / 30)), top + boxH), outline=255, fill=255)

    cV = "%.0f FPS" % streamFps
    cVw, cVh = valueFont.getsize(cV)

    top = top + boxH + 2
    draw.text((height / 2 - cVw / 2, top), cV, font=valueFont, fill=255)


    cH = "ACTIVE"
    cHw, cHh = headerFont.getsize(cH)

    top = top + cVh + 6
    draw.text((height / 2 - cHw / 2, top), cH, font=headerFont, fill=255, spacing=4)

    cV = "%d" % sessions
    cVw, cVh = splashFont.getsize(cV)

    top = top + cHh + 2
    draw.text((height / 2 - cVw / 2, top), cV, font=splashFont, fill=255)


    rot = image.crop((0, 0, height, top + cVh)).rotate(90, expand=1)
    sx, sy = rot.size

    finalDraw.rectangle((0, 0, width, height), outline=0, fill=0)
    final.paste(rot,(0, 0, sx, sy), rot)

    # Display image.
    disp.image(final)
    disp.show()

    # print("---------------------------------------")
    # print("http://%s:%d" % (hostname, port), flush=False)
    # print("CPU @ %.2f%% busy" % cpu, flush=False)
    # print("Encoding @ %.1ffps" % encodeFps, flush=False)
    # print("%d sessions @ avg %.1ffps" % (sessions, streamFps), flush=True)

    time.sleep(5)
