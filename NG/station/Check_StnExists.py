#############################################
### CHECK IF A GIVEN STATION EXISTS IN NG ###
#############################################

import requests

def checkIfStationExists(station, tokenNG, server_pub):
    # check if the station exist already
    stnIdUrl = server_pub + "GetLocationData?LocationIdentifier=" + str(station) + "&token=" + tokenNG
    try:
        r = requests.get(stnIdUrl)
        if r.status_code == 200:
            print ("Station exists: " + str(station))
            return 1
        else:
            return 0
    except:
        print ("Station does not exists: " + str(station))
        return 0