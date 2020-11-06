def getCorrections(token, timeseriesID, fromDate, toDate):
    '''
    Get raw list of corrections from AQ NG
    :param timeseriesID: ID of specific timeseries (station@time.series)
    :param fromDate: date to collect corrections from.
    :return: raw corrections list in json format
    '''
    command = "http://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2/GetCorrectionList"
    params = {"token": token, "TimeSeriesUniqueId": timeseriesID, 'QueryFrom': fromDate, 'QueryTo': toDate}

    r = requests.get(command, params)
    json_data = r.json()
    return json_data