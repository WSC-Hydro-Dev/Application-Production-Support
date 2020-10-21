##################################################################################
### DAILY EMAILER TO SEND SUMMARY OF CDP STATUS BASED ON THE RESULT OF AWS_CDP ###
##################################################################################

import boto3
import requests
from datetime import datetime
from botocore.exceptions import ClientError

userName = "USERNAME"
password = "PASSWORD"
server_pub = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"

path = "PATH"
excelPath = path + "CDPgoogle.xlsx"
emailLog = open(path + "emailLog.txt", "a+")

class Station:
    def __init__(self, stationID, tsParameter, rule, value, email):
        self.stationID = stationID
        self.tsParameter = tsParameter
        self.rule = rule
        self.value = value
        self.email = email


class Email:
    def __init__(self, emailAddress,  message):
        self.emailAddress = emailAddress
        self.message = message


stationNoData = []

# get stations that need to send out notification
def loadDataGap():
    with open(path + 'CDP_report.txt') as fp:
        line = fp.readline()
        while line:
            stationNoData.append(line)
            line = fp.readline()


def loadThreshold():
    with open(path + 'threshold_data.txt') as fp:
        line = fp.readline()
        while line:
            stationNoData.append(line)
            line = fp.readline()


def emailing(send):
    message = send.message
    BODY_HTML = """\
            <html>
              <body>
                <p>
                    This is a daily summary email about the status of your stations. <br>
                    The following notifications were triggered:
                    <br></br> 
                    ================================================
                    <br></br> 
                    {message}
                    <br></br> 
                    ================================================
                    <br></br>
                    To modify a notification rule, please visit 
                    URL TO CONFLUENCCE
                    <br></br>
                    Please do not reply to this email. For any issues, please submit on confluence:
                    URL TO TICKETS ON JIRA
                </p>
              </body>
            </html>
            """.format(message=message)

    SENDER = "SENDER EMAIL"
    RECIPIENT = send.emailAddress
    AWS_REGION = "us-east-1"

    SUBJECT = "CDP Daily Notification"

    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          region_name=AWS_REGION,
                          aws_access_key_id='AWS ACCESS KEY',
                          aws_secret_access_key='AWS SECRET ACCESS KEY'
                          )

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
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
        emailLog.write(e.response['Error']['Message'] + "\n")
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        emailLog.write("Email sent to: " + str(send.emailAddress) + "\n")


def getFullName(stnId, token):
    Url = server_pub + "GetLocationDescriptionList?LocationIdentifier=" + str(stnId) + "&token=" + token
    try:
        r = requests.get(Url)
        stationName = r.json()['LocationDescriptions'][0]['Name']
        fullName = str(stnId + " - " + stationName)
        return fullName
    except:
        print ("Unable to get station name for: " + str(stnId))
        return 1


def groupData(stationNoData, token):
    length = len(stationNoData)
    print (length)
    if length != 0:
        for row in stationNoData:
            emailTo = row.split(",")
            primaryEmail = str(emailTo[4]).replace("\n", "")
            fullStnName = getFullName(emailTo[0], token)
            if fullStnName != 1:
                content = str(emailTo[2]).replace("{Value}", emailTo[3]).replace(":", "") + " for " + emailTo[1] + " at " + fullStnName
            else:
                content = str(emailTo[2]).replace("{Value}", emailTo[3]).replace(":", "") + " for " + emailTo[
                    1] + " at " + emailTo[0]
            stationNoData.remove(row)
            break
        tobeRemoved = []
        if len(stationNoData) != 0:
            for row in stationNoData:
                data = row.split(",")
                techEmail = str(data[4]).replace("\n", "")
                if techEmail == primaryEmail:
                    stnName = getFullName(data[0], token)
                    if stnName != 1:
                        line = str(data[2]).replace("{Value}", data[3]).replace(":", "") + " for " + data[1] + " at " + stnName
                    else:
                        line = str(data[2]).replace("{Value}", data[3]).replace(":", "") + " for " + data[1] + " at " + data[0]
                    content = content + ";<br>" + line
                    tobeRemoved.append(row)
        send = Email(primaryEmail, content)
        emailing(send)

        for row in tobeRemoved:
            if row in stationNoData:
                stationNoData.remove(row)

        if len(stationNoData) != 0:
            groupData(stationNoData, token)
    print("Done")


def getLoginToken(userName, password, server_pro):
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token


def main():
    print("Start!!")
    emailLog.write("++++++++++++++++++++++++++++++++++++++++++++++\nDaily Email started at: " + str(datetime.now()) + " - UTC" + "\n")
    token = getLoginToken(userName, password, server_pro)
    loadDataGap()
    loadThreshold()
    groupData(stationNoData, token)


if __name__ == "__main__":
    main()