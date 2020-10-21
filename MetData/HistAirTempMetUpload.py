#############################################################################################
# DOWNLOAD AIR TEMP DATA FROM 3.10 THEN UPLOAD TO NG (ONE TIME PROCESS FOR HISTORICAL DATA) #
#############################################################################################
import csv
import StringIO
import requests
import os
import datetime

parameter = "Air Temp"
userName = "USERNAME"
password = "PASSWORD"
server_pub = "http://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"
server_acq = "https://wsc.aquaticinformatics.net/AQUARIUS/Acquisition/v2/"
log = open("C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\log.txt", "a+")

def getStationIds():
    stationIds = []
    # Read text file to get all the station IDs
    path = "C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\"

    exists = False
    if os.path.isfile(path + 'stationList.txt'):
        exists = True
        print ("File exist")
    else:
        print ("File not exist")
        exists = False

    # Read stations in the file and append it to station ID list
    if exists:
        with open(path + 'stationList.txt') as fp:
            line = fp.readline()
            while line:
                stationIds.append(line)
                line = fp.readline()

    return stationIds


def getLoginTT():
    # login to 3.10
    loginUrl = "http://wwghwpapp1.mb.ec.gc.ca/aquarius/Publish/AquariusPublishRestService.svc/GetAuthToken?user=USERNAME&encPwd=PASSWORD"
    r = requests.get(loginUrl)
    token = r.text
    return token


def downloadAirTempData(stations, tokenTT):
    for station in stations:
        station = station.replace("\n", "")
        print "+++ download met data from 3.10 for station: " + str(station)
        # get met station info
        locationUrl = "http://wwghwpapp1.mb.ec.gc.ca/aquarius/Publish/AquariusPublishRestService.svc/GetLocations?token=" + tokenTT + "&filter=Identifier=" + station
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
        startDate = datetime.datetime(2020, 3, 1, 1, 0, 0, 0)
        endDate = datetime.datetime(2020, 4, 26, 1, 0, 0, 0)

        Timeseries = "Air Temp.DAILY MEAN TEMPERATURE@" + str(station)

        command = "http://wwghwpapp1.mb.ec.gc.ca/aquarius/Publish/AquariusPublishRestService.svc/GetTimeSeriesRawData?token=" + tokenTT + "&dataId=" + Timeseries
        command = command + "&queryFrom=" + str(startDate) + "&queryTo=" + str(endDate)
        try:
            r = requests.get(command)
        except:
            continue
        result = r.status_code
        resultText = r.text
        print station + "  " + str(result)

        if result == 200:
            outputResultFile(station, stationName, lat, long, resultText)
        else:
            file = open("C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\NoMetAirTemp.txt", "a+")
            file.write(str(station) + "\n")
            print "No Air Temp data for " + str(station)


def outputResultFile(station, stationName, lat, long, resultText):
    # append to newStationFile list and output it as a .txt
    newStationFile = []
    newStationFile.append(
        str(station).replace("\n", "") + ", " + str(stationName) + "," + str(lat) + "," + str(long) + "\n")
    file = open("C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\TTresultListAirTemp.txt", "a+")
    for m in newStationFile:
        for n in m:
            file.write(n)
    file.close()

    outputPath = "C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\TTdownload"
    outputFile = open(outputPath + "\\" + station + "_airTemp.txt", "w+")
    for m in resultText:
        for n in m:
            outputFile.write(n)
    outputFile.close()


def getToken(userName, password):
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token


def getResultStations():
    TTResultList = []
    # Read stations in the file and append it to TTResultList list
    with open("C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\TTresultListAirTemp.txt") as fp:
        line = fp.readline()
        while line:
            id = line.split(",")
            TTResultList.append(id[0])
            line = fp.readline()
    return TTResultList


def getStationDetails(stn):
    with open("C:\\Users\\YanX\\Desktop\\scripts\\\MetData\\TTresultListAirTemp.txt") as fp:
        line = fp.readline()
        while line:
            line_s = line.split(",")
            id = line_s[0]
            if id == str(stn):
                stationName = line_s[1]
                lat = line_s[2]
                long = line_s[3]
                return stationName, lat, long
                continue
            line = fp.readline()


def checkIfStationExists(station, tokenNG, server_pub):
    # chech if the station exist already
    stnIdUrl = server_pub + "GetLocationData?LocationIdentifier=" + str(station) + "&token=" + tokenNG
    try:
        r = requests.get(stnIdUrl)
        if r.status_code == 200:
            print "Station exists: " + str(station)
            return 1
        else:
            return 0
    except:
        print "Station does not exists: " + str(station)
        return 0


def createNGstation(station, stationName, lat, long, userName, password, tokenNG, server_pub, server_pro):
    exists = checkIfStationExists(station, tokenNG, server_pub)
    if exists == 0:
        # create the met station with info extracted from 3.10 in NG
        stnUrl = server_pro + "locations"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        data = '{"UtcOffset": "", "LocationIdentifier": "' + station + '", "LocationName": "' + stationName + '", "LocationPath": "WSC", "LocationType": "Meteorology Station", ' \
                '"Description": "", "Longitude": ' + long + ', "Latitude": ' + lat + ', "ElevationUnits": "m", "Elevation": 0, "ExtendedAttributeValues":null}'

        try:
            r = requests.post(stnUrl, data=data, headers=headers, auth=(userName, password))
            print "Create station in NG: " + str(station)
            log.write(str(station) + " -- Created --" + str(r.status_code) + "\n")
        except:
            print "Failed to create station in NG: " + str(station)
            log.write(str(station) + " -- Failed to Create" + str(r.status_code) + "\n")


def getStationUniqueId(stn, token, server_pub):
    stnIdUrl = server_pub + "GetLocationData?LocationIdentifier=" + str(stn) + "&token=" + token
    exists = False
    try:
        r = requests.get(stnIdUrl)
        exists = True
        print "Station exists: " + str(stn)
    except:
        print "Station does not exists: " + str(stn)

    # get the unique Id of the station
    try:
        r = requests.get(stnIdUrl)
        UniqueId = r.json()['UniqueId']
        return UniqueId
    except:
        print "Unable to get Unique Id for station: " + str(stn)
        log.write("Unable to get stn unique id for station: " + str(stn))


def createNGTimeSerie(stn, stationUniqueId, userName, password, server_pro):
    # Create Time Series
    tsUrl = server_pro + "locations/" + str(stationUniqueId) + "/timeseries/basic"

    TSdata = '{"GapTolerance": "PT1441M", "LocationUniqueId": "' + str(stationUniqueId) + '", "Label": "Air Temperature", "Parameter": "TA",' \
                    ' "Unit": "degC", "InterpolationType": "InstantaneousValues", "SubLocationIdentifier": "", "UtcOffset": "", "Publish": false,' \
                    '"Description": "", "Comment": "", "Method": "DefaultNone", "ComputationIdentifier": "", "ComputationPeriodIdentifier": "", "ExtendedAttributeValues":null}'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        r = requests.post(tsUrl, data=TSdata, headers=headers, auth=(userName, password))
        print "TS created for station: " + str(stn)
        log.write("TS created for station: " + str(stn) + "\n")
    except:
        print "Unable to create TS for station: " + str(stn)
        log.write("Unable to create TS for station: " + str(stn) + "\n")


def getTimeSerieUniqueId(stn, tokenNG, server_pub):
    tsIdUrl = server_pub + "GetTimeSeriesDescriptionList?LocationIdentifier=" + str(stn) + "&token=" + tokenNG
    try:
        r = requests.get(tsIdUrl)
        TSUniqueId = r.json()['TimeSeriesDescriptions'][0]['UniqueId']
        return TSUniqueId
    except:
        print "Unable to get Unique Id for station: " + str(stn)
        log.write("Unable to get TS Unique Id for station: " + str(stn) + "\n")



def uploadMetData(stn, tsUniqueId, username, password, server_acq):
    # import the file with air temperature and parse dates and values
    data = []
    airPath = "C:\\Users\\YanX\\Desktop\\scripts\\MetData\\TTdownload\\"
    with open(airPath + str(stn) + '_airTemp.txt') as fp:
        line = fp.readline()
        line = fp.readline()
        line = fp.readline()
        line = fp.readline()
        line = fp.readline()
        line = fp.readline()
        while line:
            data.append(line)
            line = fp.readline()

    for x in data:
        try:
            y = x.split(",")
            time = str(y[1])[:19] + "Z"
            value = y[2]
            print time
            url = server_acq + "timeseries/" + str(tsUniqueId) + "/append"
            Udata = '{"UniqueId": "' + str(tsUniqueId) + '", "Points": [{"Time": "' + time + '", "Value": ' + value + ', "Type": "Point", "GradeCode": -1, "Qualifiers": ""}]}'
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            try:
                r = requests.post(url, data=Udata, headers=headers, auth=(username, password))
            except:
                print "Unable to upload TS data to NG for station: " + str(stn)
            print r.status_code
        except:
            continue


def main():
    print "Start!!"
    stations = getStationIds()
    tokenTT = getLoginTT()
    downloadAirTempData(stations, tokenTT)
    resultStns = getResultStations()
    tokenNG = getToken(userName, password)
    for stn in resultStns:
        log.write(str(stn))
        stn = stn.replace("\n", "")
        stationName, lat, long = getStationDetails(stn)
        createNGstation(stn, stationName, lat, long, userName, password, tokenNG, server_pub, server_pro)
        stationUniqueId = getStationUniqueId(stn, tokenNG, server_pub)
        createNGTimeSerie(stn, stationUniqueId, userName, password, server_pro)
        tsUniqueId = getTimeSerieUniqueId(stn, tokenNG, server_pub)
        uploadMetData(stn, tsUniqueId, userName, password, server_acq)

if __name__ == "__main__":
    main()
