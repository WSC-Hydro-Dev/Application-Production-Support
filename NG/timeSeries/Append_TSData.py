import requests

def appendTSData(server_acq, tsUniqueId, time, value, username, password, stn):
    try:
        url = server_acq + "timeseries/" + str(tsUniqueId) + "/append"
        Udata = '{"UniqueId": "' + str(tsUniqueId) + '", ' \
                '"Points": [{"Time": "' + time + '", "Value": ' + value + ', "Type": "Point", "GradeCode": -1, "Qualifiers": ""}]}'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        try:
            r = requests.post(url, data=Udata, headers=headers, auth=(username, password))
        except:
            print ("Unable to upload TS data to NG for station: " + str(stn))
        print (r.status_code)
    except:
        print("Oops")