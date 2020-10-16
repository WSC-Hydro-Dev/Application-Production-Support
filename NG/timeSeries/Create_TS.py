# NEED ADMIN ACCOUNT AND PLEASE CHECK GAPTOLERANCE, LABEL INTERPOLATIONTYPE AND PARAMETER.
# MIGHT NEED TO CREATE NEW PARAMETER TO BE ABLE TO USE THIS. THE FOLLOWING IS AN EXAMPLE FOR PRECIPITATION TIMESERIES.
import requests
def createNGTimeSerie(stn, stationUniqueId, userName, password, server_pro):
    # Create Time Series
    tsUrl = server_pro + "locations/" + str(stationUniqueId) + "/timeseries/basic"

    TSdata = '{"GapTolerance": "PT1441M", "LocationUniqueId": "' + str(stationUniqueId) + '", "Label": "Total Precipitation", "Parameter": "PPT",' \
                    ' "Unit": "mm", "InterpolationType": "InstantaneousValues", "SubLocationIdentifier": "", "UtcOffset": "", "Publish": false,' \
                    '"Description": "", "Comment": "", "Method": "DefaultNone", "ComputationIdentifier": "", "ComputationPeriodIdentifier": "", "ExtendedAttributeValues":null}'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        r = requests.post(tsUrl, data=TSdata, headers=headers, auth=(userName, password))
        print ("TS created for station: " + str(stn))
    except:
        print ("Unable to create TS for station: " + str(stn))