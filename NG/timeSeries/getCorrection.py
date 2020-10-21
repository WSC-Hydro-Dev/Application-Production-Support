import json
from datetime import datetime as dt, datetime, time

import requests

AQ_time = '%Y-%m-%dT%H:%M:%S'
AQ_base_url = 'https://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2/'

# Get correction data
def getCorrection(stationId, s):
    #Get recent corrections
    url = (AQ_base_url+'GetTimeSeriesDescriptionList?LocationIdentifier='+stationId)
    response = s.get(url)
    data = json.loads(response.text)
    stageID = '' #UniqueIDs are needed for the corrections
    dischargeID = '' #dischargeID is also useful to know whether to try and get a rating curve
    for i in data['TimeSeriesDescriptions']:
        if i['Identifier'] == 'Discharge.Working@'+stationId:
            dischargeID = i['UniqueId']
        elif i['Identifier'] == 'Stage.Working@'+stationId:
            stageID = i['UniqueId']
    correction_list = [['Applied', 'Type', 'Data', 'Comment', 'Start', 'End']]
    stationOff = False
    if stageID != '':
        url = (AQ_base_url+'GetCorrectionList?TimeSeriesUniqueId='+stageID)
        response = s.get(url)
        data = json.loads(response.text)
        for i in data['Corrections']:
            cor_type = i['Type']
            cor_start = dt.strptime(i['StartTime'][:19],AQ_time)
            cor_end = dt.strptime(i['EndTime'][:19],AQ_time)
            if cor_end.year == 9999:
                #for ongoing corrections, convert to future
                #date that pandas/numpy can actually handle
                cor_end = datetime.datetime(2262,1,1)
            cor_applied = dt.strptime(i['AppliedTimeUtc'][:19],AQ_time)
            cor_comment = i['Comment']
            cor_user = i['User']
            correction_list.append([cor_applied,cor_type,'HG',cor_comment,cor_start,cor_end])
            #Check if station is active
            if cor_user != "Migration" and cor_type == "DeleteRegion":
                if cor_start <= dt.today() <= cor_end:
                    stationOff = True
    if dischargeID != '':
        url = (AQ_base_url+'GetCorrectionList?TimeSeriesUniqueId='+dischargeID)
        response = s.get(url)
        data = json.loads(response.text)
        for i in data['Corrections']:
            cor_type = i['Type']
            cor_start = dt.strptime(i['StartTime'][:19],AQ_time)
            cor_end = dt.strptime(i['EndTime'][:19],AQ_time)
            if cor_end.year == 9999:
                #for ongoing corrections, convert to future
                #date that pandas/numpy can actually handle
                cor_end = datetime.datetime(2262,1,1)
            cor_applied = dt.strptime(i['AppliedTimeUtc'][:19],AQ_time)
            cor_comment = i['Comment']
            cor_user = i['User']
            correction_list.append([cor_applied,cor_type,'Q',cor_comment,cor_start,cor_end])
            print("here")


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


def main():
    print("Start!!")
    token = getToken('USERNAME', 'PASSWORD', 'https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/')
    getCorrection("05MJ001", token)

if __name__ == "__main__":
    main()