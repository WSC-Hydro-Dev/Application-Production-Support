import requests

def createNGstation(station, stationName, lat, long, userName, password, server_pro):
    # create the met station with info extracted from 3.10 in NG
    stnUrl = server_pro + "locations"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    data = '{"UtcOffset": "", "LocationIdentifier": "' + station + '", "LocationName": "' + stationName + '", "LocationPath": "WSC", "LocationType": "Meteorology Station", ' \
                '"Description": "", "Longitude": ' + long + ', "Latitude": ' + lat + ', "ElevationUnits": "m", "Elevation": 0, "ExtendedAttributeValues":null}'

    try:
        r = requests.post(stnUrl, data=data, headers=headers, auth=(userName, password))
        print ("Create station in NG: " + str(station))
    except:
        print ("Failed to create station in NG: " + str(station))