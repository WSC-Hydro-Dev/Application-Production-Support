import requests
import json
import re
from datetime import datetime as dt
from dateutil.parser import parse

stations = []
fieldVisitInfoList = []

with open('C:\Users\YanX\Desktop\scripts\Reports\FullStation.csv') as fp:
    line = fp.readline()
    while line:
        data = line.split(",")
        stations.append(data[1])
        line = fp.readline()

Server = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"
reportToYear = parse("2020/09/30")
reportFromYear = parse("2020/01/01")

# Login
def getToken():
    userName = "USERNAME"
    password = "PASSWORD"
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token


def appendData(token):
    for station in stations:
        station = station[1:8]
        print (station)
        # High level information
        try:
            req = requests.get(Server + 'GetLocationData?LocationIdentifier=' + station + '&token=' + token)
            locationData = req.json()
            province = locationData['ExtendedAttributes'][0]['Value']
            office = locationData['ExtendedAttributes'][1]['Value']
            stnId = station
            stnName = locationData['LocationName']
        except:
            print ("Failed to load location Data for Station:" + station)


        # Get stage & discharge
        try:
            req = requests.get(Server + 'GetFieldVisitDataByLocation?LocationIdentifier=' + station + '&token=' + token)
            fieldDescriptions = req.json()['FieldVisitData']
        except:
            print ("Failed to load Field Visit Data for Station:" + station)
            continue

        for i in range(len(fieldDescriptions)):
            fieldVisitData = fieldDescriptions[i]
            fieldId = fieldVisitData['Identifier']
            startTime = fieldVisitData['StartTime']
            start = fieldVisitData['StartTime'].replace('-', '/')
            fieldVisitDate = parse(start[0:10])
            year = str(fieldVisitDate)[0:4]
            date = str(fieldVisitDate)[5:10]

            hasReadings = False
            hasStage = False
            hasDischarge = False
            hasMGH = False
            if reportToYear >= fieldVisitDate >= reportFromYear:
                print (fieldVisitDate)
                try:
                    fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
                    hasReadings = True
                except:
                    pass

                if hasReadings:
                    if len(fieldVisitReadings) != 0:
                        print ("hasReading")

                        try:
                            # check if MGH exists
                            mgh = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeanGageHeight']['Numeric']
                            hasMGH = True
                        except:
                            pass

                        if hasMGH:
                            stage = mgh
                        else:
                            try:
                                fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
                                hasStage = True
                            except:
                                pass

                            if hasStage:
                                logger = ''
                                for i in fieldVisitReadings:
                                    if i['Parameter'] == 'Stage' and i['MonitoringMethod'] != 'Logger':
                                        try:
                                            logger = i['Value']['Numeric']
                                        except:
                                            pass
                                stage = logger
                            else:
                                stage = " "
                                pass

                        # discharge
                        try:
                            # check if discharge exists
                            fieldVisitDischarge = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['Discharge']['Numeric']
                            hasDischarge = True
                        except:
                            fieldVisitDischarge = " "
                            pass
                    else:
                        pass
                else:
                    pass

                fieldVisitInfoList.append(str(year) + ',')
                fieldVisitInfoList.append(str(date) + ',')
                fieldVisitInfoList.append(str(province) + ',')
                fieldVisitInfoList.append(str(office) + ',')
                fieldVisitInfoList.append(str(stnId) + ',')
                fieldVisitInfoList.append(str(stnName.encode('utf-8').replace('\xc8', 'E')) + ',')
                fieldVisitInfoList.append(str(stage) + ',')
                fieldVisitInfoList.append(str(fieldVisitDischarge) + ',')
                fieldVisitInfoList.append(' ' + '\n')

    path = 'C:\_dev'
    if len(fieldVisitInfoList) > 0:
        while True:
            try:
                print ("output file")
                outputfile = open(path + '\\' + "FVReport" + "1020.csv", "wb")
                outputfile.write(
                    'Year, Date, Province, Office, Station ID, Station Name, Stage|m, Discharge|m^3/s\n')
                for m in fieldVisitInfoList:
                    for n in m:
                        outputfile.write(n)
                outputfile.close()
                break
            except IOError:
                print ("Could not open file! Please close Excel!")
                break
    print ("DONE")


def main():
    print("Start!!")
    token = getToken()
    appendData(token)

if __name__ == "__main__":
    main()