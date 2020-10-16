# DOWNLOAD MET DATA FROM 3.10 EXAMPLE WITH PRECIPITATION DATA
import csv
import datetime
from io import StringIO
import requests

def downloadPrecipData(stations, tokenTT):
    # get met station info
    locationUrl = "" + tokenTT + "&filter=Identifier=" + stations
    r = requests.get(locationUrl)
    f = StringIO.StringIO(unicode(r.text).encode("utf8"))
    reader = csv.reader(f, delimiter=',')
    reader.next()
    line = reader.next()

    stationName = line[3]
    utcOffset = line[12]
    lat = line[7]
    long = line[8]

    # get Air temp from 3.10
    startDate = datetime.datetime(2015, 1, 1, 1, 0, 0, 0)
    endDate = datetime.datetime(2020, 3, 1, 1, 0, 0, 0)

    Timeseries = "Precip Inc.DAILY TOTAL PRECIPITATION@"+str(stations)

    command = "" + tokenTT + "&dataId=" + Timeseries
    command = command + "&queryFrom=" + str(startDate) + "&queryTo=" + str(endDate)
    try:
        r = requests.get(command)
    except:
        print ("something is wrong")
    result = r.status_code
    resultText = r.text

    if result == 200:
        # DO SOMETHING
        print("do something with it")
    else:
        file.write(str(stations) + "\n")
        print "No Precip data for " + str(stations)