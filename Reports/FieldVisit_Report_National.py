import requests
import json
import re
from datetime import datetime as dt
from dateutil.parser import parse

#path = 'PATH TO CSV WITH ALL STATIONS ID'
#username = 'USERNAME'
#password = 'PASSWORD'
reportToYear = parse("2020/01/01")
reportFromYear = parse("2019/01/01")
Server = "http://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"


def getStations(path):
    stations = []
    with open(path) as fp:
        line = fp.readline()
        while line:
            data = line.split(",")
            stations.append(data[1].replace('"', ''))
            line = fp.readline()
    return stations


def generateReport(stationIDs, token):
    # for each station
    fieldVisitInfoList = []
    for station in stationIDs:
        # load the all field visit for one station into json file
        print (station)
        try:
            req = requests.get(Server + 'GetFieldVisitDataByLocation?LocationIdentifier=' + station + '&token=' + token)
            fieldDescriptions = req.json()['FieldVisitData']
        except:
            print ("Failed to load Field Visit Data for Station:" + station)
            continue

        try:
            req = requests.get(Server + 'GetLocationData?LocationIdentifier=' + station + '&token=' + token)
            locationName = req.json()['LocationName']
        except:
            print ("Failed to get station name for station:" + station)
            continue

        # final list
        # for each field visit
        for i in range(len(fieldDescriptions)):
            fieldVisitData = fieldDescriptions[i]
            fieldId = fieldVisitData['Identifier']
            startTime = fieldVisitData['StartTime']
            start = fieldVisitData['StartTime'].replace('-', '/')
            fieldVisitDate = parse(start[0:10])

            print (fieldVisitDate)

            hasReadings = False
            hasStage = False
            hasDischarge = False
            hasMGH = False
            if reportFromYear <= fieldVisitDate <= reportToYear:
                # look for reading for the field visit
                try:

                    fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
                    hasReadings = True
                except:
                    pass

                if hasReadings:
                    if len(fieldVisitReadings) != 0:

                        fieldDataStagelist = []
                        fieldDateDischargelist = []
                        print ("hasReading")
                        # Stage
                        try:
                            # check if MGH exists
                            fieldVisitStage = \
                            fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeanGageHeight']['Numeric']
                            hasMGH = True
                        except:
                            pass

                        # if stage exists then append info to the list
                        if hasMGH:
                            locationId = station
                            date = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][0:10]
                            activity = "Stage"
                            meanTime = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][
                                       11:19]
                            tz = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][-6:]
                            discharge = ''
                            RcNo = ''
                            shift = ''
                            controlCond = ''
                            try:
                                activityRemark = fieldVisitData['Remarks']
                            except:
                                activityRemark = ''
                            locationRemark = ''
                            activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                            fieldDataStagelist.append(str(locationId) + ',')
                            fieldDataStagelist.append(str(locationName) + ',')
                            fieldDataStagelist.append(str(date) + ',')
                            fieldDataStagelist.append(str(activity) + ',')
                            fieldDataStagelist.append(str(meanTime) + ',')
                            fieldDataStagelist.append(str(tz) + ',')
                            fieldDataStagelist.append(str(fieldVisitStage) + ',')
                            fieldDataStagelist.append(str(discharge) + ',')
                            fieldDataStagelist.append(str(RcNo) + ',')
                            fieldDataStagelist.append(str(shift) + ',')
                            fieldDataStagelist.append(str(controlCond) + ',')
                            fieldDataStagelist.append(
                                str(activityRemark).replace(",", "").replace("\n", " ").replace("\r", " ").replace(
                                    "==Aggregated measurement activity remarks:  ", "") + ',')
                            fieldDataStagelist.append(str(locationRemark) + ',')
                            fieldDataStagelist.append(' ' + '\n')
                            fieldVisitInfoList.append(fieldDataStagelist)
                            print ("Add MGH")
                        else:
                            try:
                                fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
                                hasStage = True
                            except:
                                pass

                            if hasStage:
                                fieldVisitStage = ''
                                readingComments = ''
                                readingTime = ''
                                for i in fieldVisitReadings:
                                    if i['Parameter'] == 'Stage' and i['MonitoringMethod'] != 'Logger':
                                        fieldVisitStage = i['Value']['Numeric']
                                        readingTime = i['Time']
                                        try:
                                            readingComments = i['Comments']
                                        except:
                                            readingComments = ""
                                stage1 = fieldVisitStage
                                comments = readingComments
                                if fieldVisitStage == "":
                                    activity = "No Stage or Discharge Measurement"
                                else:
                                    activity = "Stage"

                                locationId = station
                                if readingTime != '':
                                    date = readingTime[0:10]
                                    meanTime = readingTime[11:19]
                                    tz = readingTime[-6:]
                                else:
                                    date = startTime[0:10]
                                    meanTime = startTime[11:19]
                                    tz = startTime[-6:]
                                discharge = ''
                                RcNo = ''
                                shift = ''
                                controlCond = ''
                                try:
                                    activityRemark = fieldVisitData['Remarks']
                                except:
                                    activityRemark = ''
                                locationRemark = ''
                                activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                                fieldDataStagelist.append(str(locationId) + ',')
                                fieldDataStagelist.append(str(locationName) + ',')
                                fieldDataStagelist.append(str(date) + ',')
                                fieldDataStagelist.append(str(activity) + ',')
                                fieldDataStagelist.append(str(meanTime) + ',')
                                fieldDataStagelist.append(str(tz) + ',')
                                fieldDataStagelist.append(str(stage1) + ',')
                                fieldDataStagelist.append(str(discharge) + ',')
                                fieldDataStagelist.append(str(RcNo) + ',')
                                fieldDataStagelist.append(str(shift) + ',')
                                fieldDataStagelist.append(str(controlCond) + ',')
                                fieldDataStagelist.append(
                                    str(activityRemark).replace(",", "").replace("\n", " ").replace("\r", " ").replace(
                                        "==Aggregated measurement activity remarks:  ", "") + ',')
                                fieldDataStagelist.append(str(locationRemark) + ',')
                                fieldDataStagelist.append(' ' + '\n')
                                fieldVisitInfoList.append(fieldDataStagelist)
                                print ("Add Stage")

                        # discharge
                        try:
                            # check if discharge exists
                            fieldVisitDischarge = \
                            fieldVisitData['DischargeActivities'][0]['DischargeSummary']['Discharge']['Numeric']
                            hasDischarge = True
                        except:
                            pass

                        if hasDischarge:
                            locationId = station
                            date = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][0:10]
                            activity = "Discharge"
                            meanTime = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][
                                       11:19]
                            tz = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][-6:]
                            if hasMGH:
                                stage = fieldVisitStage
                            else:
                                stage = stage1
                            formattedDischarge = []
                            formattedDischarge.append(fieldVisitDischarge)

                            # get shift
                            try:
                                shiftreq = requests.get(
                                    Server + "GetRatingModelInputValues?RatingModelIdentifier=""Stage-Discharge.Rating Curve@" + station + "&OutputValues=" + str(
                                        fieldVisitDischarge) + "&EffectiveTime=" + date + "&token=" + token)
                                # shiftreq = requests.get(Server+"GetRatingModelInputValues?RatingModelIdentifier=Stage-Discharge.Rating%20Curve%4001DC007&OutputValues=80.7&EffectiveTime=2019-09-10&token="+token)
                                unshiftedStage = shiftreq.json()['InputValues'][0]
                            except:
                                unshiftedStage = None
                                print ("error while getting unshifted value")
                            print (stage)
                            if unshiftedStage != None and stage != '':
                                shift = stage - unshiftedStage
                            else:
                                shift = 'N/A'
                            # get rc no
                            try:
                                rcreq = requests.get(
                                    Server + "GetRatingCurveList?RatingModelIdentifier=""Stage-Discharge.Rating Curve@" + station + "&QueryFrom=" + date + "&QueryTo=" + date + "&token=" + token)
                                rc = rcreq.json()['RatingCurves'][0]['Id']
                            except:
                                rc = ''
                                print ("error while getting rating curve number")

                            rcId = rc

                            # control condition
                            try:
                                controlCond = fieldVisitData['ControlConditionActivity']['ControlCondition']
                            except:
                                controlCond = ''

                            # activityRemark
                            try:
                                activityRemark = fieldVisitData['Remarks']
                            except:
                                activityRemark = ''
                            locationRemark = ''
                            activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                            fieldDateDischargelist.append(str(locationId) + ',')
                            fieldDateDischargelist.append(str(locationName) + ',')
                            fieldDateDischargelist.append(str(date) + ',')
                            fieldDateDischargelist.append(str(activity) + ',')
                            fieldDateDischargelist.append(str(meanTime) + ',')
                            fieldDateDischargelist.append(str(tz) + ',')
                            fieldDateDischargelist.append(str(stage) + ',')
                            fieldDateDischargelist.append(str(fieldVisitDischarge) + ',')
                            fieldDateDischargelist.append(str(rcId) + ',')
                            fieldDateDischargelist.append(str(shift) + ',')
                            fieldDateDischargelist.append(str(controlCond) + ',')
                            fieldDateDischargelist.append(
                                str(activityRemark).replace(",", "").replace("\n", " ").replace("\r", " ").replace(
                                    "==Aggregated measurement activity remarks:  ", "") + ',')
                            fieldDateDischargelist.append(str(locationRemark) + ',')
                            fieldDateDischargelist.append(' ' + '\n')
                            fieldVisitInfoList.append(fieldDateDischargelist)
                            print ("Add Discharge")
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
    path = "C:\\_dev"
    if len(fieldVisitInfoList) > 0:
        while True:
            try:
                print ("output file")
                outputfile = open(path + '\\' + "AnnualFV" + "_test", "wb")
                outputfile.write(
                    'Location ID, Location Name, Date, Activity, Time, UTC offset, Stage|m, Discharge|m^3/s, RC No, Shift, Control Condition, Activity Remarks, Location Remarks\n')
                for m in fieldVisitInfoList:
                    for n in m:
                        outputfile.write(n)
                outputfile.close()
                break
            except IOError:
                print ("Could not open file! Please close Excel!")
                break
    print ("DONE")


def getToken(userName, password):
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token


def main():
    stationIDs = getStations(path)
    token = getToken(username, password)
    generateReport(stationIDs, token)

if __name__ == "__main__":
    main()