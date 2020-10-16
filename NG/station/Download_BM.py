import requests
import os

stations = []
failedStations = []
totalBenchmarkList = []
path = "path to your input list of stations"
outputPath = "output path"
server_pub = "URL"

s = requests.Session()
data = '{"Username": "' + "USERNAME" + '", "EncryptedPassword": "' + "PASSWORD" + '", "Locale": ""}'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
url = 'PROV URL'
try:
    s.get(url)
    aq = s.post(url, data=data, headers=headers)
    token = aq.text
except:
    print ("can't login")

if os.path.isfile(path):
    exists = True
    print ("File exist")
else:
    print ("File not exist")
    exists = False
# Read stations in the file and append it to station ID list
if exists:
    with open(path) as fp:
        line = fp.readline()
        while line:
            stations.append(line.replace("\r\n", ""))
            line = fp.readline()


for station in stations:
    station = str(station).replace("\n", "")
    print (str(station))
    try:
        req = requests.get(server_pub + "GetLocationData?LocationIdentifier=" + station + "&token=" + token)
        staInfo = req.json()['ReferencePoints']
    except:
        failedStations.append(station)
        print("failed: " + str(station))

    # print staInfo
    for benchMark in staInfo:
        benchMarkInfo = []
        decommissioned = False
        try:
            decom = benchMark['DecommissionedDate']
            decommissioned = True
        except:
            decommissioned = False

            if not decommissioned:
                try:
                    staRef = unicode(benchMark['Name'])
                    staRef.replace('\n', ' ')
                except:
                    staRef = ''
                    print("The reference is empty.")

                try:
                    pmyRef = benchMark['PrimarySinceDate']
                    staRef = "**" + str(staRef)
                except:
                    pmyRef = ''

                outputLine = unicode(station) + "," + unicode(staRef)

                totalBenchmarkList.append(outputLine)

outputFile = open(outputPath, "w+")
for line in totalBenchmarkList:
    line += '\n'
    outputFile.write(line.encode('utf8'))
outputFile.close()
print("Done")