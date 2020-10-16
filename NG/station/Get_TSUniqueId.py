import requests

def getTimeSerieUniqueId(stn, tokenNG, server_pub, parameter):
    tsIdUrl = server_pub + "GetTimeSeriesDescriptionList?LocationIdentifier=" + str(stn) + "&token=" + tokenNG
    try:
        r = requests.get(tsIdUrl)
        TSdesc = r.json()['TimeSeriesDescriptions']
    except:
        print "Unable to get Unique Id for station: " + str(stn)

    for x in TSdesc:
        param = x['Parameter']
        if param == parameter:
            TSUniqueId = x['UniqueId']

    return TSUniqueId