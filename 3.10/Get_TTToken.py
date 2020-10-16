###########################################
### GET THE LOGIN TOKEN TO AQUARIUS 3.10###
###########################################
import requests

def getLoginTT(userName, password):
    loginUrl = "http://wwghwpapp1.mb.ec.gc.ca/aquarius/Publish/AquariusPublishRestService.svc/GetAuthToken?user=" + userName + "&encPwd=" + password
    r = requests.get(loginUrl)
    token = r.text
    return token