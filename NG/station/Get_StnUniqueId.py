##############################################
###

import requests

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