#!/usr/bin/python3
import csv
import sys
import requests
import time
import json
import simplekml

# airlog-ng
# Parses airodump-ng logcsv output into beautiful KMLs via WiGLE
#
# Copyright 2022 Alex Farrant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, 
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ssids = {}

WiGLE_key = "" # https://wigle.net/commercial
with open("api.key", 'r') as f:
    WiGLE_key = f.read().strip()

kml = simplekml.Kml()

def findLocation(bssid):
    lat=0
    lon=0
    error=0

    url = "https://api.wigle.net/api/v2/network/detail?netid=%s" % bssid
    print(url)
    time.sleep(0.1)

    #r = requests.get(url, headers={"Authorization": "Basic %s" % WiGLE_key})
    #if r.status_code == 200:
    #    print(r.text)
    #    geo = json.loads(r.text)
    geo = json.loads('{"success":true,"cdma":false,"gsm":false,"lte":false,"wcdma":false,"wifi":false,"addresses":[],"results":[{"trilat":51.86360931,"trilong":-2.11790085,"ssid":null,"qos":0,"transid":"20211102-00938","firsttime":"2020-11-20T18:56:23.000Z","lasttime":"2021-11-02T15:06:28.000Z","lastupdt":"2021-11-02T15:21:22.000Z","netid":"62:86:20:B1:7D:74","name":null,"type":"infra","comment":null,"wep":"2","bcninterval":0,"freenet":"?","dhcp":"?","paynet":"?","userfound":null,"channel":1,"locationData":[{"alt":118,"accuracy":9.648,"lastupdt":"2021-11-02T07:00:00.000Z","latitude":51.86288071,"longitude":-2.11947298,"month":"202111","ssid":null,"time":"2020-11-20T08:00:00.000Z","signal":-82.0,"name":null,"netId":"108328213642612","noise":0.0,"snr":0.0,"wep":"2","channel":0,"encryptionValue":"WPA2"},{"alt":118,"accuracy":9.648,"lastupdt":"2021-11-02T07:00:00.000Z","latitude":51.86337662,"longitude":-2.11844301,"month":"202111","ssid":null,"time":"2020-11-20T08:00:00.000Z","signal":-82.0,"name":null,"netId":"108328213642612","noise":0.0,"snr":0.0,"wep":"2","channel":0,"encryptionValue":"WPA2"},{"alt":117,"accuracy":9.648,"lastupdt":"2021-11-02T07:00:00.000Z","latitude":51.86383057,"longitude":-2.11734414,"month":"202111","ssid":null,"time":"2020-11-20T08:00:00.000Z","signal":-82.0,"name":null,"netId":"108328213642612","noise":0.0,"snr":0.0,"wep":"2","channel":0,"encryptionValue":"WPA2"},{"alt":116,"accuracy":9.648,"lastupdt":"2021-11-02T07:00:00.000Z","latitude":51.86435318,"longitude":-2.11634302,"month":"202111","ssid":null,"time":"2020-11-20T08:00:00.000Z","signal":-82.0,"name":null,"netId":"108328213642612","noise":0.0,"snr":0.0,"wep":"2","channel":0,"encryptionValue":"WPA2"}],"encryption":"wpa2","country":"GB","region":"England","city":null,"housenumber":null,"road":"Shurdington Road","postalcode":"GL51 4US"}]}')

    if geo["success"] == True and len(geo["results"]) > 0:
        for g in geo["results"]:
            #print(g)
            lat = g["trilat"]
            lon = g["trilong"]
            error = 100
            updated = g["lasttime"]
            kml.newpoint(name=bssid, coords=[(lon,lat)])

    ssids[bssid] = {"bssid": bssid, "lat": lat, "lon": lon, "error": error, "updated": updated}
    #else:
    #    print(r.status_code)
    #    print(r.text)


with open(sys.argv[1], 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar="'")
    # Save these for writing later
    header = reader.fieldnames
    table = [row for row in reader]

    # Geolocate the data
    for row in table:
        bssid = row[" BSSID"] # Watch the space!
        rssi = row[" Power"]
        role = row[" Type"]
        geoDone = 0 # So we don't waste API calls ;)
        if "Geo lookup" in row:
            geoDone = int(row["Geo lookup"])
        if role == "AP":
            if bssid not in ssids and geoDone < 1:
                #print(bssid,rssi,role)
                ssids[bssid] = {"lat":0,"lon":0,"error":0}
                findLocation(bssid)



# Write it back whence it came
with open(sys.argv[1]+".csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, header)
    if "Geo lookup" not in header:
        header.append("Geo lookup")
    writer.writeheader()
    for row in table:
        row["Geo lookup"] = "1"
        if row[" BSSID"] in ssids.keys():
            row["Geo lookup"] = "2"
            geo = ssids[row[" BSSID"]]
            #print(geo)
            row[" Latitude"] = geo["lat"]
            row[" Longitude"] = geo["lon"]
            row[" Latitude Error"] = geo["error"]
            row[" Longitude Error"] = geo["error"]

        writer.writerow(row)

kml.save(sys.argv[1]+".kml")   