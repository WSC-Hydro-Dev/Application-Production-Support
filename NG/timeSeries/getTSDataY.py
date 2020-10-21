import os

import requests
import time
import json
from datetime import datetime, timedelta

userName = "USERNAME"
password = "PASSWORD"
server_pub = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"
server_acq = "https://wsc.aquaticinformatics.net/AQUARIUS/Acquisition/v2/"
dataList = []
outputPath = 'C:\\_dev\\outputStnDataD.csv'
def getToken(userName, password, server_pro):
    t0 = time.time()
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    print("--- %s seconds ---" % (time.time() - t0))
    return token


def getStationIds(path):
    stationIds = []
    with open(path) as fp:
        line = fp.readline()

        while line:
            print(line)
            stationIds.append(line.replace('\n',''))
            line = fp.readline()

    return stationIds


def getTSUniqueID(token, stationID):
    for station in stationID:
        stnUrl = server_pub + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + station + '&Parameter=Discharge&token=' + token
        req = requests.get(stnUrl)
        data = json.loads(req.text)
        uniqueID = ''
        for i in data['TimeSeriesDescriptions']:
            if i['Identifier'] == 'Discharge.Working@' + station:
                uniqueID = i['UniqueId']
                break
    return uniqueID


def exportToCsv(dataList, outputPath):
    outputFile = open(outputPath, "w+")
    for m in dataList:
        for n in m:
            outputFile.write(str(n))
            outputFile.write(",")
        outputFile.write("\n")
    outputFile.close()


def downloadData(uniqueId, currentTime, token, stationID):
    fromTime = currentTime - timedelta(days=365)
    print (fromTime)
    formattedFromTime = str(fromTime)[:19]
    formattedToTime = str(currentTime)[:19]
    tsUrl = server_pub + 'GetTimeSeriesData?TimeSeriesUniqueIds=' + uniqueId + '&QueryFrom=' + formattedFromTime + '&QueryTo=' + formattedToTime + '&token=' + token
    req = requests.get(tsUrl)
    data = json.loads(req.text)['Points']
    for i in data:
        try:
            dataList.append([i['Timestamp'], i['NumericValue1']])
        except KeyError:
            pass

    exportToCsv(dataList, outputPath)

def main():
    print("Start!!")
    token = getToken(userName, password, server_pro)
    path = 'C:\\_dev\\stationProgramID.txt'
    # stationID = getStationIds(path)
    stationID = ['05AA008']
    currentTime = datetime.now()
    print(currentTime)
    uniqueId = getTSUniqueID(token, stationID)
    print(uniqueId)
    downloadData(uniqueId, currentTime, token, stationID)

if __name__ == "__main__":
    main()