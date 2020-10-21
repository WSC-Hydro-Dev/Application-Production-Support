#########################################################################
### CDP SCRIPT TO CHECK IF A STATION HAVE A RECEIVED DATA IN THE PASS ###
### 6 HOURS AND IF THE STAGE VALUE IS > OR < THE PREDEFINED THRESHOLD ###
#########################################################################

import os
from datetime import datetime, timedelta

import boto3
import pandas as pd
import requests

# need xlrd, openpyxl
from botocore.exceptions import ClientError

#### REMEMBER TO REMOVE /r BECAUSE OF PYTHON VERSION
path = "/home/ubuntu/"
excelPath = path + 'CDPgoogle.xlsx'
log = open(path + "stageLog.txt", "a+")
emailLog = open(path + "emailLog.txt", "a+")

userName = "USERNAME"
password = "PASSWORD"
server_pub = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"
server_acq = "https://wsc.aquaticinformatics.net/AQUARIUS/Acquisition/v2/"

url = 'CDP AUTO EMAILER NOTIFICATIONS URL'

stationNoData = []
stationRemoved = []
stations = []
stationAdded = []
thresholdStations = []
sysUTCtime = datetime.utcnow()
sheetName = ["", "", ""]

thresholdData = []
thresholdRemoved = []
thresholdAdded = []


# If its not the first time that this is run, then we need to load stations that are already in the list to not spam emails to DCS
exists = False
if os.path.isfile(path + 'CDP_report.txt'):
    exists = True
    print ("File exist")
else:
    print ("File not exist")
    exists = False

# If the file exists then load station in the file to the list to add or remove station later on
if exists:
    with open(path + 'CDP_report.txt') as fp:
        line = fp.readline()
        while line:
            stationNoData.append(line)
            line = fp.readline()


with open(path + 'threshold_data.txt') as fp:
    line = fp.readline()
    while line:
        thresholdData.append(line)
        line = fp.readline()

class Station:
    def __init__(self, stationID, tsParameter, rule, value, email):
        self.stationID = stationID
        self.tsParameter = tsParameter
        self.rule = rule
        self.value = value
        self.email = email


def getToken(userName, password, server_pro):
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token


def populateStationList():
    xls = pd.ExcelFile(excelPath)
    Stage = pd.read_excel(xls, 'Stage Notifications', header=None)
    # NorthBay = pd.read_excel(xls, 'North Bay', header = None)
    Sheet1 = Stage.to_csv(index=False)

    dataSheet = Sheet1.split("\n")
    int = 0
    for line in dataSheet:
        if int < 2:
            pass
            int += 1
        else:
            if line != '' or None:
                lineData = line.split(",")
                stations.append(str(lineData[1].upper() + "," + lineData[2] + "," + lineData[3] + "," +
                                    lineData[4] + "," + lineData[5]) + "\n")
                thresholdStations.append(str(lineData[1].upper() + "," + lineData[2] + "," + lineData[3] + "," +
                                             lineData[4] + "," + lineData[5]) + "\n")


def downloadCSV():
    resp = requests.get(url)
    output = open(excelPath, 'wb')
    output.write(resp.content)
    output.close()
    print("File Downloaded")
    log.write("File Downloaded" + "\n")

    populateStationList()


def appendData(line):
    line = line.split(",")
    stationId = line[1].upper()
    tsParameter = line[2]
    rule = line[3]
    value = line[4]
    techEmail = line[5]
    dcsEmail = line[6]
    additionalEmail = line[7]
    if techEmail == "#N/A"  or techEmail == '' or techEmail == ' ':
        if dcsEmail == '':
            if additionalEmail == '':
                email = 'xu.yan@canada.ca'
            else:
                email = additionalEmail
        else:
            email = dcsEmail
            if additionalEmail != '':
                email = email + "," + additionalEmail
    else:
        email = techEmail
        if dcsEmail != '':
            email = email + "," + dcsEmail
        if additionalEmail != '':
            email = email + "," + additionalEmail

    stationData = Station(stationId, tsParameter, rule, value, email)
    return stationData


def getTsDescription(stationData, token):
    try:
        req = requests.get(
            server_pub + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + stationData.stationID + '&token=' + token)
        TimeSeriesDescriptions = req.json()['TimeSeriesDescriptions']
        return TimeSeriesDescriptions
    except:
        print("Unable to retrieve Time Series data for station:" + str(stationData.stationID))
        log.write("Unable to retrieve Time Series data for station:" + str(stationData.stationID))
        return 0


def getlastModifiedcriteriaTime(stationData, appliedRule):
    if stationData.value == '' or None:
        lastModifiedcriteriaTime = sysUTCtime - timedelta(hours=6)
    else:
        lastModifiedcriteriaTime = sysUTCtime - timedelta(hours=int(stationData.value))
    return lastModifiedcriteriaTime


def evaluateGapTS(stationData, lastModifiedcriteriaTime, tsDescription, appliedRule, token):
    for i in range(len(tsDescription)):
        tsIdentifier = tsDescription[i]["Identifier"]
        try:
            UTCoffset = tsDescription[i]["UtcOffset"]
        except:
            UTCoffset = 0
        offset = abs(UTCoffset)
        if tsIdentifier == stationData.tsParameter + "@" + stationData.stationID:
            try:
                CorrectedEndTime = tsDescription[i]["CorrectedEndTime"].replace("T", " ")[0:26]
                CorrectedEndTime = datetime.strptime(CorrectedEndTime, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=offset)
            except:
                CorrectedEndTime = datetime.strptime('1000-01-01 01:01:00.00000', '%Y-%m-%d %H:%M:%S.%f')
            if CorrectedEndTime < lastModifiedcriteriaTime:
                return str("NoData") # No data
            else:
                return str("Data") # Data


def evaluateThresholdTS(stationData, lastModifiedcriteriaTime, tsDescription, appliedRule, token):
    for i in range(len(tsDescription)):
        tsIdentifier = tsDescription[i]["Identifier"]
        tsUniqueId = tsDescription[i]["UniqueId"]
        if tsIdentifier == stationData.tsParameter + "@" + stationData.stationID:
            if stationData.value is None or stationData.value == "":
                pass
            else:
                tsDataUrl = server_pub + 'GetTimeSeriesData?TimeSeriesUniqueIds=' + str(
                    tsUniqueId) + '&QueryFrom=' + str(lastModifiedcriteriaTime)[:19] + '&token=' + token
                try:
                    req = requests.get(tsDataUrl)
                    tsData = req.json()['Points']
                except:
                    print("Unable to get TS data for station:" + str(stationData.stationID))
                    log.write("Unable to get TS data for station:" + str(stationData.stationID) + "\n")
                if tsData != 0:
                    length = len(tsData)
                    if length != 0:
                        lastDataPoint = tsData[length - 1]
                        recentValue = lastDataPoint['NumericValue1']
                        if stationData.rule == 'Data is greater than {Value} in meters' and recentValue >= float(stationData.value):
                            return "Above"
                        if stationData.rule == 'Data is less than {Value} in meters' and recentValue < float(stationData.value):
                            return "Below"

def evaluateGapList(stationData, stationNoData):
    if str(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n") in stationNoData:
        return str("Yes")
    else:
        return str("No")


def evaluateThresholdList(stationData, thresholdData):
    if str(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n") in thresholdData:
        return str("Yes")
    else:
        return str("No")


def email(stationData):
    stationNum = stationData.stationID
    code = "https://hydex.cmc.ec.gc.ca/en/reports/station/station_description?stations[]=" + stationNum
    threshold = stationData.value

    SENDER = "SENDER EMAIL ADDRESS"
    RECIPIENT = str(stationData.email).split(",")
    receiver = []
    for x in RECIPIENT:
        print (x[-10:])
        if str(x[-10:]) == "@canada.ca":
            receiver.append(x)
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = "Notification for: " + stationNum
    if "gap" in stationData.rule:
        BODY_TEXT = """\
        Your station has not recieved data in the last while - you should check on it.
        Here is the station description report: {code}
        """.format(code=code)
        BODY_HTML = """\
        <html>
          <body>
            <p>
               Stage.Working @{stationNum} has not received data in the last 6 hours.
               <br></br>
               Check the <a href="{code}">HYDEX Report</a> to ensure HYDEX is correct (e.g., set this station discontinued, inactive, or a seasonal if necessary)
               <br></br>
               Here is the link to <a href="URL TO AQ">Aquarius</a>
               <br></br>
               Stations are checked hourly.  This email will not be sent again, however a summary of all stations that have not received data will be sent nightly.
                <br></br>
                To modify a notification rule, please visit 
                URL TO CONFLUENCE
                <br></br>
               Please do not reply to this email. For any issues, please submit on confluence:
               URL TO TICKETS ON JIRA
            </p>
          </body>
        </html>
        """.format(code=code, stationNum=stationNum)
    if "greater" in stationData.rule:
        BODY_TEXT = """\
                Your station stage is greater than {threshold} - you should check on it.
                """.format(code=code, threshold = threshold)
        BODY_HTML = """\
                <html>
                  <body>
                    <p>
                       Stage.Working @{stationNum} has a stage greater than {threshold}.
                       <br></br>
                       Check the <a href="{code}">HYDEX Report</a> to ensure HYDEX is correct (e.g., set this station discontinued, inactive, or a seasonal if necessary)
                       <br></br>
                       Here is the link to <a href="URL TO AQ">Aquarius</a>
                       <br></br>
                       Stations are checked hourly.  This email will not be sent again.
                        <br></br>
                        To modify a notification rule, please visit 
                        URL TO CONFLUENCE
                        <br></br>
                       Please do not reply to this email. For any issues, please submit on confluence:
                       URL TO TICKET ON JIRA
                    </p>
                  </body>
                </html>
                """.format(code=code, stationNum=stationNum, threshold = threshold)

    if "less" in stationData.rule:
        BODY_TEXT = """\
                Your station stage is less than {threshold} - you should check on it.
                """.format(code=code, threshold = threshold)
        BODY_HTML = """\
                <html>
                  <body>
                    <p>
                       Stage.Working @{stationNum} is less than {threshold}.
                       <br></br>
                       Check the <a href="{code}">HYDEX Report</a> to ensure HYDEX is correct (e.g., set this station discontinued, inactive, or a seasonal if necessary)
                       <br></br>
                       Here is the link to <a href="URL TO AQ">Aquarius</a>
                       <br></br>
                       Stations are checked hourly.  This email will not be sent again.
                        <br></br>
                        To modify a notification rule, please visit 
                        URL TO CONFLUENCCE
                        <br></br>
                       Please do not reply to this email. For any issues, please submit on confluence:
                       URL TO JIRA
                    </p>
                  </body>
                </html>
                """.format(code=code, stationNum=stationNum, threshold = threshold)

    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          region_name=AWS_REGION,
                          # free tier
                          aws_access_key_id='AWS ACCESS KEY',
                          aws_secret_access_key='AWS SECRETE ACCESS KEY'
                          #m5.large

                          )

    for x in receiver:
        try:
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        x,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
                # If you are not using a configuration set, comment or delete the
                # following line
                # ConfigurationSetName=CONFIGURATION_SET,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
            log.write(e.response['Error']['Message'] + "\n")
        else:
            print("Email sent! Message ID:")
            print(response['MessageId'])
            log.write("Email sent to: " + str(x) + "for station: " + stationData.stationID + "\n")
            emailLog.write("Email sent to: " + str(x) + "for station: " + stationData.stationID + "\n")


def getAppliedRule(stationData):
    if stationData.rule == "Data gap exceeds {Value} in hours:":
        return "gap"
    else:
        return "threshold"


def checkTS(stationData, token, stationNoData, thresholdData):
    appliedRule = getAppliedRule(stationData)
    tsDescription = getTsDescription(stationData, token)
    if appliedRule == "gap":
        lastModifiedcriteriaTime = getlastModifiedcriteriaTime(stationData, appliedRule)
        if tsDescription != 0:
            inList = evaluateGapList(stationData, stationNoData)
            resultGap = evaluateGapTS(stationData, lastModifiedcriteriaTime, tsDescription, appliedRule, token)
            if inList == "Yes":
                if resultGap == "Data":
                    stationRemoved.append(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n")
                    stationNoData.remove(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n")
                elif resultGap == "NoData":
                    pass
            elif inList == "No":
                if resultGap == "Data":
                    pass
                elif resultGap == "NoData":
                    print("Need to send an email")
                    log.write("Need to send an email for " + stationData.stationID + " | " + stationData.rule + " | " + stationData.value + "\n")
                    stationNoData.append(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n")  # Add to list
                    stationAdded.append(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule +
                                          "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n")
                    email(stationData)
        else:
            print("TS for " + str(stationData.tsParameter) + "doesn't exists for station: " + str(stationData.stationID))
            log.write("TS for " + str(stationData.tsParameter) + "doesn't exists for station: " + str(
                stationData.stationID) + "\n")

    if appliedRule == "threshold":
        lastModifiedcriteriaTime = sysUTCtime - timedelta(hours=13)
        if tsDescription != 0:
            inList = evaluateThresholdList(stationData, thresholdData)
            inGapList = evaluateGapList(stationData, stationNoData)
            resultTh = evaluateThresholdTS(stationData, lastModifiedcriteriaTime, tsDescription, appliedRule, token)
            if inList == "Yes":
                if inGapList == "Yes":
                    pass
                else:
                    if resultTh == "Above" or resultTh == "Below":
                        pass
                    else:
                        thresholdData.remove(str(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n"))
                        thresholdRemoved.append(str(stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + "," + stationData.value + "," + str(stationData.email).split(",")[0] + "\n"))
            elif inList == "No":
                if inGapList == "Yes":
                    pass
                else:
                    if resultTh == "Above":
                        print("Station Stage above: " + str(stationData.value))
                        thresholdData.append(str(
                            stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + ","
                            + stationData.value + "," + str(stationData.email).split(",")[0] + "\n"))  # Add to list
                        thresholdAdded.append(str(
                            stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + ","
                            + stationData.value + "," + str(stationData.email).split(",")[0] + "\n"))  # Add to list
                        log.write("Station " + stationData.stationID + "stage above: " + stationData.value + "\n")
                        email(stationData)
                    if resultTh == "Below":
                        print("Station Stage below: " + str(stationData.value))
                        thresholdData.append(str(
                            stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + ","
                            + stationData.value + str(stationData.email).split(",")[0] + "\n"))  # Add to list
                        thresholdAdded.append(str(
                            stationData.stationID + "," + stationData.tsParameter + "," + stationData.rule + ","
                            + stationData.value + "," + str(stationData.email).split(",")[0] + "\n"))  # Add to list
                        log.write("Station " + stationData.stationID + "stage above: " + stationData.value + "\n")
                        email(stationData)
                    else:
                        pass
        else:
            print("TS for " + str(stationData.tsParameter) + "doesn't exists for station: " + str(stationData.stationID))
            log.write("TS for " + str(stationData.tsParameter) + "doesn't exists for station: " + str(
                stationData.stationID) + "\n")


def checkStnExists(stationID, token):
    stnIdUrl = server_pub + "GetLocationData?LocationIdentifier=" + str(stationID) + "&token=" + token
    try:
        r = requests.get(stnIdUrl)
        if r.status_code == 200:
            return 1
        else:
            return 0
    except:
        print("Can't find Station: " + str(stationID))
        log.write("Can't find station: " + str(stationID) + "\n")
        return 0


def checkStation(stationData, token, stationNoData, thresholdData):
    stnUniqueId = checkStnExists(stationData.stationID, token)
    if stnUniqueId != 0:
        checkTS(stationData, token, stationNoData, thresholdData)
    else:
        print("Station not found in AQ NG")
        log.write("Station not found in AQ NG" + "\n")


def readNverifyData(token, stationNoData, thresholdData):
    xls = pd.ExcelFile(excelPath)
    Stage = pd.read_excel(xls, 'Stage Notifications', header = None)
    # NorthBay = pd.read_excel(xls, 'North Bay', header = None)
    Sheet1 = Stage.to_csv(index= False)
    print("CSV")

    dataSheet = Sheet1.split("\n")
    int = 0
    for line in dataSheet:
        if int < 2:
            pass
            int += 1
        else:
            if line != '' or None:
                lineData = line.split(",")
                if lineData[4] == '' or lineData[4] == ' ' or None:
                    print(str(lineData[1].upper() + "," + lineData[2]) + " do not notify")
                    log.write(str(lineData[1].upper() + "Value empty" + "\n"))
                    continue
                else:
                    print(str(lineData[1].upper() + "," + lineData[2]))
                    stationData = appendData(line)
                    checkStation(stationData, token, stationNoData, thresholdData)


def evaluatePreviousRun():
    for x in stationNoData:
        if x not in stations:
            stationRemoved.append(x)
            print("This station has been updated in spreedsheet: " + str(x))
            log.write("This station has been updated in spreedsheet: " + str(x))

    for station in stationRemoved:
        data = station.split(",")
        if (data[0] + "," + data[1] + "," + data[2] + "," + data[3] + "," + data[4]) in stationNoData:
            stationNoData.remove(data[0] + "," + data[1] + "," + data[2] + "," + data[3] + "," + data[4])

    for x in thresholdData:
        if x not in thresholdStations:
            thresholdRemoved.append(x)
            print("This threshold has been updated in spreedsheet: " + str(x))
            log.write("This threshold has been updated in spreedsheet: " + str(x))

    for station in thresholdRemoved:
        # data = station.split(",")
        # if (data[0] + "," + data[1]) in thresholdData:
        if station in thresholdData:
            thresholdData.remove(station)


def outputFile(stationNoData, stationRemoved):
    if len(stationNoData) > 0:
        while True:
            try:
                print("output file")
                log.write("output CDP file")
                outputfile = open(path + 'CDP_report.txt', "w+")
                for m in stationNoData:
                    for n in m:
                        outputfile.write(n)
                outputfile.close()
                break
            except IOError:
                print("Could not open CDP_Report! Please close the file!")
                break

    if len(thresholdData) > 0:
        while True:
            try:
                log.write("output Threshold data")
                outputfile = open(path + 'threshold_data.txt', "w+")
                for m in thresholdData:
                    for n in m:
                        outputfile.write(n)
                outputfile.close()
                break
            except IOError:
                print("Could not open threshold data! Please close the file!")
                break

    f = open(path + "log.txt", "a+")
    print("Logging")
    log.write("output log file")
    f.write("CDP checker finished running at: " + str(datetime.now()) + "EST" + "\n")
    f.write("New added stations: " + "\n")
    for m in stationAdded:
        for n in m:
            f.write(n)
        f.writelines("\n")
    f.writelines("Stations removed: " + "\n")
    for m in stationRemoved:
        for n in m:
            f.write(n)
        f.writelines("\n")
    f.writelines("Threshold added: " + "\n")
    for m in thresholdAdded:
        for n in m:
            f.write(n)
        f.writelines("\n")
    f.writelines("threshold removed: " + "\n")
    for m in thresholdRemoved:
        for n in m:
            f.write(n)
        f.writelines("\n")
    f.writelines("===========================================================" + "\n")
    f.close()

def main():
    print("Start!!")
    log.write("=======================================================\nCDP checker started at: " + str(datetime.now()) + "UTC" + "\n")
    emailLog.write("=======================================================\nCDP checker started at: " + str(datetime.now()) + "UTC" + "\n")
    token = getToken(userName, password, server_pro)
    downloadCSV()
    # populateStationList()
    evaluatePreviousRun()
    readNverifyData(token, stationNoData, thresholdData)
    outputFile(stationNoData, stationRemoved)

if __name__ == "__main__":
    main()