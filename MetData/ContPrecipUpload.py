######################################################
# GET DAILY PRECIP DATA FROM GEOMET AND UPLOAD TO NG #
######################################################
import requests
import os
from dateutil.parser import parse

def getStationIds():
    # Get all station listed in the text file
    stations = []
    path = "PATH"
    exists = False
    if os.path.isfile('PATH TO STATION LIST'):
        exists = True
        print ("File exist")
    else:
        print ("File not exist")
        exists = False

    if exists:
        with open(path + '\\TTresultListPrecip.txt') as fp:
            line = fp.readline()
            while line:
                stations.append(line)
                line = fp.readline()
    return stations

def getLogin():
    # login to Aquarius
    s = requests.Session()
    data = '{"Username": "USERNAME", "EncryptedPassword": "PASSWORD", "Locale": ""}'
    url = 'https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token

def getEndTime(station, parameter, token):
    # Get the last time the Times Series is updated
    Server = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
    stationID = station.split(",")[0]
    try:
        req = requests.get(Server + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + stationID + '&Parameter=' + parameter + '&token=' + token)
        TSDescription = req.json()['TimeSeriesDescriptions']
        endTime = TSDescription[0]['CorrectedEndTime']
        return endTime
    except:
        print "Failed:" + station
        return 0

def getGeoMetData(station, parameter, EndTime, token):
    # Get data from GeoMet
    formattedEndTime = parse(str(EndTime[0:10]))
    print formattedEndTime
    api_url = 'https://geo.weather.gc.ca/geomet/features/collections/climate-daily/items'
    params = {
        'CLIMATE_IDENTIFIER': station,
        'f': 'json',
        'limit': 10000
    }
    TSId = getTsId(station, parameter, token)
    stnData = requests.get(api_url, params=params).json()['features']
    for x in stnData:
        date = parse(str(x['properties']['LOCAL_DATE'][0:10]))
        if date >= formattedEndTime:
            precip = x['properties']['TOTAL_PRECIPITATION']
            uploadTempToNg(TSId, precip, date)

def uploadTempToNg(TSId, precip, date):
        url = "https://wsc.aquaticinformatics.net/AQUARIUS/Acquisition/v2/timeseries/" + str(TSId) + "/append"
        Udata = '{"UniqueId": "' + str(TSId) + '", "Points": [{"Time": "' + str(date) + '", "Value": ' + str(precip) + ', "Type": "Point", "GradeCode": -1, "Qualifiers": ""}]}'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        try:
            r = requests.post(url, data=Udata, headers=headers, auth=('USERNAME', 'PASSWORD'))
        except:
            print "Error occured while appending data to TS:" + str(TSId)
        print str(date) + " --> "+ str(r.status_code)

def getTsId(station, parameter, token):
    # Get time series ID
    Server = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
    stationID = station.split(",")[0]
    try:
        req = requests.get(
            Server + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + stationID + '&Parameter=' + parameter + '&token=' + token)
        TSDescription = req.json()['TimeSeriesDescriptions']
    except:
        print "Failed: " + station

    TSUniqueId = TSDescription[0]['UniqueId']
    return TSUniqueId


def main():
    print "Start!!"
    stations = getStationIds()
    token = getLogin()
    parameter = "Precip Total"

    for station in stations:
        print "++++++++++++++++++++++++++++++++++++++++++++"
        print station
        station = station.replace("\n", "")
        endTime = getEndTime(station, parameter, token) # 2020-02-02T00:00:00.0000000+00:00
        if endTime != 0:
            getGeoMetData(station, parameter, endTime, token)

if __name__ == "__main__":
    main()