import requests

def getTsDescription(server_pub, token, stationId):
    try:
        req = requests.get(
            server_pub + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + str(stationId) + '&token=' + token)
        TimeSeriesDescriptions = req.json()['TimeSeriesDescriptions']
        return TimeSeriesDescriptions
    except:
        print("Unable to retrieve Time Series data for station:" + str(stationId))
        return 0