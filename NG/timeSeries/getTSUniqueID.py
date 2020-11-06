def getTimeSeriesUniqueID(token, station, type):
    '''
    Get the unique id for a timeseries, to reference later
    :param station: station id #
    :param type: Type of timeseries to aquire (EX. Stage.Working)
    :return:
    '''
    command = "http://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2/GetTimeSeriesDescriptionList"
    params = {"token": token, "LocationIdentifier": station}

    dataId = type + '@' + station
    r = requests.get(command, params)
    json_data = r.json()

    UniqueId = None
    for timeseries in json_data["TimeSeriesDescriptions"]:
        if dataId in timeseries['Identifier']:
            UniqueId = timeseries['UniqueId']
            break

    if UniqueId == None:
        print("Error getting {}".format(dataId))

    return UniqueId