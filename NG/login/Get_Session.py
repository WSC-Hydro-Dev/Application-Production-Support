###################################
### GET SESSION FOR AQUARIUS NG ###
###################################
import requests

def getSession(userName, password, server_pro):
    s = requests.Session()
    url = server_pro + 'session'
    s.post(url)
    return s