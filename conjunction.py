#!/usr/bin/env python

"""
conjuction.py

Find conjuctions of the given objects, as seen from the given
location, within the given range of time...

Objects can be anything know by PyEphem, or RA/DEC from the J2000
epoch.

Location can be anything known to 'geocoder.google()'.  Basically,
anything that you can find on maps.google.com.

Start can either be 'now', or a date and time that ephem.Date()
understands.  YYYY/MM/DD HH:MM:SS works.

Duration and Resolution can be a time including Nd (or N d, or Ndays,
etc.), Nh (or hours, etc.), Nm (...), and Ns (...).  All are optional
and the order doesn't matter.

As an example,

conjunction.py --objects Jupiter Moon --where Rowlett --start now --duration "20d" --resolution "1m"
--------------- setup ---------------
   Objects: [<ephem.Jupiter "Jupiter" at 0x7f1dfd8885f0>, <ephem.Moon "Moon" at 0x7f1dfd381340>]
  Location: <ephem.Observer date='2017/4/24 16:45:29' epoch='2000/1/1 12:00:00' lon='-96:33:50.0' lat='32:54:10.4' elevation=153.7m horizon=0:00:00.0 temp=15.0C pressure=0.0mBar>
Start Time: 2017/4/24 16:45:29
  Duration: 1728000
Resolution: 60
--------------- results ---------------
Minimum: 1 degrees 46 minutes 16.36 seconds at 2017/5/7 21:03:29
Maximum: 177 degrees 33 minutes 25.27 seconds at 2017/4/25 03:41:29
"""

import argparse
import ephem
import ephem.stars
import geocoder
import math
import re

from math import *

################################################################################
## Parse Arguments

parser = argparse.ArgumentParser(description='Conjuction Finder')
parser.add_argument('--objects', nargs="*", type=str,
                    help='List of objects, separated by spaces, to use.')
parser.add_argument('--where', type=str,
                    help='The position of the observer.')
parser.add_argument('--start', type=str,
                    help='When to start.')
parser.add_argument('--duration', type=str,
                    help='How long to run.')
parser.add_argument('--resolution', type=str,
                    help='How often to check.')
args = parser.parse_args()

################################################################################
# Convert a time string to seconds.

def strToSeconds(s):
    seconds = int(0)

    # Days
    m = re.search("([0-9]+)d", s)
    if m:
        seconds += int(m.group(1)) * 24 * 60 * 60

    # Hours
    m = re.search("([0-9]+)h", s)
    if m:
        seconds += int(m.group(1)) * 60 * 60

    # Minutes
    m = re.search("([0-9]+)m", s)
    if m:
        seconds += int(m.group(1)) * 60

    # Seconds
    m = re.search("([0-9]+)s", s)
    if m:
        seconds += int(m.group(1))

    return seconds

################################################################################
# Convert DD to DMS

def ddToDms(dd = 0.0):
    if type(dd) != 'float':
        try:
            dd = float(dd)
        except:
            print '\nERROR: Could not convert %s to float.' %(type(dd))
            return 0

    minutes = dd % 1.0 * 60
    seconds = minutes % 1.0 * 60
    
    return '%s degrees %s minutes %s seconds' \
        %(int(floor(dd)), int(floor(minutes)), round(seconds, 2))

### Objects should be a list of solar system objects and stars.  Only
### the stars know to phEphem are supported.  The objects that have
### their own class are as follows.

objects = []

# The list of "object" available as classes in PyEphem.
solar = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
         'Uranus', 'Neptune', 'Pluto', 'Phobos', 'Deimos', 'Io', 'Europa',
         'Ganymede', 'Callisto', 'Mimas', 'Enceladus', 'Tethys', 'Dione',
         'Rhea', 'Titan', 'Hyperion', 'Iapetus', 'Ariel', 'Umbriel', 'Titania',
         'Oberon', 'Miranda']

# Create a list of the stars available, by name, in PyEphem.
stars = []

for star in ephem.stars.db.split("\n"):
    stars.append(star.split(",")[0])

# Create a list of PyEphem objects based on the list from the command line.
for object in args.objects:
    if object in solar:
        objects.append(getattr(ephem, object)())
    elif object in stars:
        objects.append(ephem.star(object))
    else:
        # Assume the RA and DEC from the J2000 epoch in the following
        # format: RA/DEC.
        ra,dec = object.split("/")
        new = ephem.FixedBody()
        new._ra = ra
        new._dec = dec
        new.name = str(object)
        objects.append(new)

### Where can be either the name of a ciy or latitute, longitude, and
### elevation.

location = geocoder.google(args.where)
elevation = geocoder.elevation(args.where)
observer = ephem.Observer()
observer.lon = math.radians(location.latlng[1])
observer.lat = math.radians(location.latlng[0])
observer.elev = elevation.meters
observer.pressure = 0

### Start is the date/time to start looking for conjuctions.

if args.start == "now":
    start = ephem.now()
else:
    start = ephem.Date(args.start)

### Duration is the amount of time to look.

duration = args.duration.replace(" ", "")
duration = strToSeconds(duration)

### Resolution is the amount of time to skip.

resolution = args.resolution.replace(" ", "")
resolution = strToSeconds(resolution)

################################################################################
## Do Something "Useful"

# output = "--------------- conjuction.py ---------------\n" \
#          "Objects: " + objects + "\n" \
#          "Location: " + observer + "\n" \
#          "Start Time: " + str(start) + "\n"
#
#"Duration: " + str(duration) + " seconds\n" \
#         "Resolution: " + str(resolution) + " seconds"

print("--------------- setup ---------------")
print("   Objects: " + str(objects))
print("  Location: " + str(observer))
print("Start Time: " + str(start))
print("  Duration: " + str(duration))
print("Resolution: " + str(resolution))

if len(objects) != 2:
    print("Can only handle 2 objects: " + str(len(object)))

a = objects[0]
b = objects[1]
t = start
end = ephem.Date(start + (float(duration) / float(24 * 60 * 60)))
min = (float(2 * math.pi), t)
max = (float(0), t)

while t.real < end.real:
    observer.date = str(t)
    a.compute(observer)
    b.compute(observer)
    sep = float(ephem.separation((a.az, a.alt), (b.az, b.alt)))

    if sep < min[0]:
        min = (sep, t)
    if sep > max[0]:
        max = (sep, t)

    t = ephem.Date(t + (float(resolution) / float(24 * 60 * 60)))

print "--------------- results ---------------"
print "Minimum: " + ddToDms(math.degrees(min[0])) + " at " + str(min[1])
print "Maximum: " + ddToDms(math.degrees(max[0])) + " at " + str(max[1])
