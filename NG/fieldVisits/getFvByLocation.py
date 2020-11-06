def getVisitByLocation(token, station):
    '''
    Get field visit raw data from AQ NG
    :param station: station id#
    :return: raw data in json format
    '''
    command = "http://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2/GetFieldVisitDataByLocation"
    params = {"token": token, "LocationIdentifier": station}

    r = requests.get(command, params)
    json_data = r.json()
    return json_data