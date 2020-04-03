#!/usr/bin/env python
import sys
import os
import subprocess
import re
import argparse
import numpy as np
import ugradio
from ugradio.interf import Interferometer, AZ_MIN, AZ_MAX
import astropy.time as at
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Galactic
from astropy import units as u
from astropy.time import Time
import traceback
import time
""" Program to capture data from radio interferometer via digital sampling

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "kyle miller"
__copyright__ = "Copyright 2020, Kyle Miller"
__date__ = "2020/02/22"
__license__ = "GPLv3"
__status__ = "alpha"
__version__ = "0.0.1"



def capture(loc, duration, celestialbody, errors):
    '''Capture data from HP Multimeter, uses tracking module'''

    # logistics for storing data capture
    file_name = None # change this later to expand functionality
    if file_name is None:
        file_name = str(get_time(unix=get_time())) + "jd"

    # capture data
    ifm = Interferometer()
    # run capture scipt (not currently working)
    #if errors == 0:
    #    subprocess.Popen(['python', 'hpcapture.py'], close_fds=True)
    start = get_time()
    intendedpositions = []
    actualpositions = []
    # run subprocess script
    while(get_time()-start < duration):
        '''main tracking cycle'''
        # start cycle timer
        cstart = get_time()
        
        # get current ra/dec of celestialbody
        if celestialbody != None:
            if celestialbody == 'moon':
                vector = ugradio.coord.moonpos(get_time(unix=get_time())) # should have location, defaults to nch
            elif celestialbody == 'sun':
                vector = ugradio.coord.sunpos(get_time(unix=get_time()))
            else:
                j2000 = celestialbody
                pra, pdec  = ugradio.coord.precess(j2000[0], j2000[1])
                vector = (pra, pdec)

        # reposition telescope taking into account limits of alt-az mount
        eqvector = ugradio.coord.get_altaz(vector[0], vector[1])   
        az = eqvector[1]
        alt = eqvector[0]
        if j2000:
            print(f"target was at ra={j2000[0]} dec={j2000[1]} [J2000]")
            print(f"target at ra={vector[0]} dec={vector[1]}")
        print(f"target at az={az} alt={alt}")
        if az < AZ_MIN:
            az = az + 180
            alt = 180 - alt
        elif az > AZ_MAX:
            az = az - 180
            alt = 180 - alt

        if alt < 5:
            print('[[OBJECT BELOW TELESCOPE HORIZON]]')
            break

        # slew
        ifm.point(alt, az)
        pointing = ifm.get_pointing()
        print(f"telescope pointing at {pointing}")
        intendedpositions.append((alt, az))
        actualpositions.append(pointing)
        # check cycle time and delay if needed
        cfinish = get_time()
        cycle = cfinish-cstart
        print(f"cycle took {cycle} seconds")
        if(cycle < 10):
            print("sleeping")
            time.sleep(10 - cycle)

    # tracking completed, get total time        
    finish = get_time()



    # save data
    print("data capture finished")
    tag_data(file_name, start, finish)
    np.savez('intendedpositionsfile', intendedpositions)
    np.savez('actualpositionsfile', actualpositions)
    print("tag file written")


    
def tag_data(fname, start, finish):
    '''Tag data capture with a text file containing time/data/location information'''
    # make output file name
    ofname = "tagfile-" + fname

    # try to get internet information with curl
    iinfo=True
    try:
        # get ip address
        ip = subprocess.Popen(["curl",  "-s", "https://ipinfo.io/ip"], stdout=subprocess.PIPE)
        (ip_address, err) = ip.communicate()
        ip_address_text = ip_address.decode("utf-8").rstrip()

        # get location information
        lookup = f"http://api.geoiplookup.net/?query={ip_address_text}"
        loc = subprocess.Popen(["curl", "-s", lookup], stdout=subprocess.PIPE)
        (location_information, err) = loc.communicate()
        loc_info = location_information.decode("utf-8")

        # parse latitude
        lat_find = re.search(r'\<latitude>[\s\S]*?<\/latitude>', loc_info)
        latitude = lat_find.group()
        lat = re.sub('<[^<]+>', "", latitude)

        # parse longitude
        long_find = re.search(r'\<longitude>[\s\S]*?<\/longitude>', loc_info)
        longitude = long_find.group()
        longi = re.sub('<[^<]+>', "", longitude)    

        # parse isp
        isp_find = re.search(r'\<isp>[\s\S]*?<\/isp>', loc_info)
        internet_service_provider = isp_find.group()
        isp = re.sub('<[^<]+>', "", internet_service_provider)

        # parse city
        city_find = re.search(r'\<city>[\s\S]*?<\/city>', loc_info)
        city = city_find.group()
        cty = re.sub('<[^<]+>', "", city)

        # parse country
        country_find = re.search(r'\<countryname>[\s\S]*?<\/countryname>', loc_info)
        country = country_find.group()
        ctry = re.sub('<[^<]+>', "", country)

    except:
        iinfo = False
        print("[[ERROR GETTING INTERNET INFORMATION]]")
        pass


    # list of parameter names for data capture
    with open(ofname, 'w') as output:
        output.write(f"\n[[METADATA FOR DATA SAMPLES IN {fname}]]\n")

        # write out internet metadata
        output.write(f"{get_date()}\n")
        output.write(f"{get_date(utc=True)}\n")
        output.write(f"Sampling was started at (unix): {start}\n")
        output.write(f"Sampling was completed at (unix): {finish}\n")
        output.write(f"Data capture took: {finish - start} seconds\n")
        output.write(f"Julian date of sample: {get_time(unix=start)}\n")
        if iinfo:
            output.write(f"IP address of computer sampling: {ip_address_text}\n")
            output.write(f"ISP used for internet access: {isp}\n")
            output.write(f"Latitude: {lat}\n")
            output.write(f"Longitude: {longi}\n")
            output.write(f"Country: {ctry}\n")
            output.write(f"City: {cty}\n\n")
                

        # write out location information
        output.write(f"\n[[LOCATION INFORMATION]]\n")
        if args.lat:
            output.write(f"User input latitude: {args.lat}\n")
        if args.lon:
            output.write(f"User input longitude: {args.lon}\n")
        if location is not None:
            output.write(f"Location was set to: {args.location}\n") 
            output.write(f"lat[{location.lat}] lon[{location.lon}]\n")

        # make room for lab notes
        output.write("\n\n[[LAB NOTES]]\n")

        # end of file marker
        output.write('\neof\n')

    # tag file written    
    print(f"tag file written to {ofname}")
    
    
def coordinates(latitude, longitude):
    '''Transform coordinates to galatic coordinates'''
    c = SkyCoord(longitude, latitude, unit='deg')
    return c

def get_altaz(alt, az):
    '''Return altitude and azimuth'''
    obs = AltAz(alt=alt*u.deg, az=az*u.deg, location=nch, obstime=Time.now())
    return obs

def get_time(jd=None, unix=None):
   '''Return (current) time, in seconds since the Epoch (00:00:00 
    Coordinated Universal Time (UTC), Thursday, 1 January 1970).
    Note: unix time will be upgraded soon from 32bit to 64bit.
    Unix time is the default output; however,

    If jd is entered, unix time will be returned.
    If unix is entered, jd will be returned.
   
    Parameters
    ----------
    jd : float, julian date, default=None (i.e., now)
    unix : float, unix time

    Returns
    -------
    time : float, seconds since the Epoch or jd of unix time'''

   if jd is not None:
       t = at.Time(jd, format='jd')
       return t.unix
      
       
   elif unix is not None:
       t = at.Time(unix, format='unix')
       return t.jd
    
   else:
       t = time.time()
       return t

   
def get_utc():
    utc = Time.now()
    return utc


def get_lst():
    lst = 0 # need to implement this
    return lst

def get_date(utc=False):
    if utc:
        date = subprocess.Popen(["date",  "-u"], stdout=subprocess.PIPE)
        (date, err) = date.communicate()
        date_text = date.decode("utf-8").rstrip()
        return date_text
    else:
        date = subprocess.Popen(["date"], stdout=subprocess.PIPE)
        (date, err) = date.communicate()
        date_text = date.decode("utf-8").rstrip()
        return date_text

        
   
# main program implemented as boiler plate logic
if __name__ == "__main__":

   # nch location
   nch = EarthLocation(lat="37.8732", lon="-122.2573", height=123.1*u.m)
   
   # argparse stuff
   parser = argparse.ArgumentParser(description='''Program used to capture data via digital sampling''')
   parser.add_argument('-loc', "--location", type=str, help="[string] enter location instead of lat, lon. Format: 'address, city, state', e.g., 'University Dr., Berkeley, CA'")
   parser.add_argument('-lt', "--lat", type=float, help="[float] takes in latitude")
   parser.add_argument('-lg', "--lon", type=float, help="[float] takes in longitude")
   parser.add_argument('-ra', "--rightascention", type=float, help="[float] take in right ascention")
   parser.add_argument('-dec', "--declination", type=float, help="[float] take in declination")
   parser.add_argument('-c', "--capture", action="store_true", help="captures data")
   parser.add_argument('-cb', "--celestialbody", type=str, help="[string] input specific celestial body [sun, moon]")
   parser.add_argument('-dt', "--trackduration", type=int, help="[int] sets time to track for")
   parser.add_argument('-t', "--time", action="store_true", help="prints the current time. Unix, utc, and local system time.")
   args = parser.parse_args()

   '''print time if toggled'''
   if args.time:
      print(f"The current unix time is: {get_time()}")
      print(f"The current UTC time is: {get_utc()}")
      print(f"The current local system time is: {get_date()}")


   # check for proper lat-lon values
   if args.lat:
       assert(-90 <= args.lat <= 90)
   if args.lon:
       assert(-180 <= args.lon <= 180) # double check this

       
   '''set location if location is toggled'''
   if args.location:
       try:
           location = EarthLocation.of_address(args.location)
           print(f"Location set to lat[{location.lat}] lon[{location.lon}]")
       except:
           print("[[LOCATION LOOKUP ERROR]]")
           sys.exit(1)
   else:
       location = nch

       
   '''check for local celetial bodies'''
   if args.celestialbody:
       if  args.celestialbody == 'sun':
           cb = 'sun'
        
       elif args.celestialbody == 'moon':
           cb = 'moon'

       elif args.celestialbody:
           try:
               obj = SkyCoord.from_name(args.celestialbody)
               cb = (obj.ra, obj.dec)
           except:
               print("[OBJECT LOOKUP ERROR]")
               sys.exit(1)
               
       else:
           '''make celestialbody  with ra and dec'''
           if args.rightascention:
               ra = args.rightascention
           else:
               print("need right ascention for tracking")
               sys.exit(1)
           if args.declination:
               dec = args.declination
           else:
               print("need declination for tracking")
               sys.exit(1)
           cb = (ra, dec)

   '''check for time duration to track'''
   if args.trackduration:
       duration = args.trackduration
   else:
       duration = 10 # default to ten seconds
            
   '''capture data if toggled'''
   if args.capture:
       begin = time.time()
       errors = 0
       elapsed = time.time()
       while((begin - elapsed) < duration):
           '''loop will make tracking continue even if there is an error'''
           try:
               capture(location,duration,cb, errors)
               break
           
           except Exception:
               print("[[DATA CAPTURE ERROR]]")
               errors += 1
               traceback.print_exc()
               elapsed = time.time()
               print(f"time was {elapsed} (unix), {errors} errors so far")
               duration = duration - (begin - elapsed)
               print(f"restarting tracking code, will continue for {duration} seconds")
               continue
