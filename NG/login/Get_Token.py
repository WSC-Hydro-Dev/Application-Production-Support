#######################################
### GET LOGIN TOKEN FOR AQUARIUS NG ###
#######################################
import requests

def getToken(userName, password, server_pro):
    s = requests.Session()
    data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
    url = server_pro + 'session'
    s.get(url)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = s.post(url, data=data, headers=headers)
    token = r.text
    return token