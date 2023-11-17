from timeseries_client import timeseries_client 
from datetime import datetime as dt

# This python script queries all section by section field visits (their station, date, and province) and stores them in a text file
# It does so by looking for the string "ADCP" in Discharge Activities -> PointVelocityDischargeActivities -> DischargeChannelMeasurement -> Comments
# of the JSON returned for the field visit using /GetFieldVisitData
# The script requires the timeseries_client module


AQ_base_url = "https://wsc.aquaticinformatics.net"


# Get the Aquarius session object
# This object will be used to send get requests to Aquarius
def getSession():

    # Credentials
    loginID = 'username' # need to be replaced by working username
    password = 'password' # need to be replaced by working password

    # Get credentials
    # This uses the python wrapper for Aquarius
    s = timeseries_client(AQ_base_url, loginID, password)

    # Return the session
    return s



def getData():
     
    # Get the Aquarius session
    s = getSession()
    file = open("SxSAquariusQueries.txt","x") # create a file to store the field visit information
    print('Script Started')

    # Example date value: "YY-mm-ddTHH:MM:SS"

    past_date = dt(2022, 6, 9) # Enter a valid date here to get SxS field visits after that date
    # today_date = dt.now()
    start_date = past_date.strftime('%Y-%m-%d')
    # end_date = today_date.strftime('%Y-%m-%d')

    parameters = {"QueryFrom": start_date}
    data = s.publish.get('/GetFieldVisitDescriptionList', params=parameters) #get all field visits on and after the start date

    for field in data["FieldVisitDescriptions"]: #loop through each field viist
        
        parameters = {'FieldVisitIdentifier': field['Identifier']}
        fieldData = s.publish.get('/GetFieldVisitData', params=parameters) #using field data identifier, get more details on each field visit

        if (len(fieldData['DischargeActivities']) > 0 and #ensure no array index out of bounds errors
            len(fieldData['DischargeActivities'][0]['PointVelocityDischargeActivities']) > 0 and 
            fieldData['DischargeActivities'][0]['PointVelocityDischargeActivities'][0]
            ['DischargeChannelMeasurement']['Comments'].find('ADCP') != -1): #make sure comments section for this data has ADCP -> indicates SxS

            file.write(field['LocationIdentifier'] + " ") #print station number

            file.write(fieldData['DischargeActivities'][0]['DischargeSummary']['MeasurementStartTime'][:10] + " ") #print date
            
            parameters={"LocationIdentifier": field['LocationIdentifier']}
            locData = s.publish.get('/GetLocationData', params=parameters)

            if locData['ExtendedAttributes'][1].get('Value') != None:
                file.write(locData['ExtendedAttributes'][1]['Value'] + '\n') #print province
            else:
                parameters={"LocationIdentifier": field['LocationIdentifier']}
                locData = s.publish.get('/GetLocationDescriptionList', params=parameters)
                file.write(locData['LocationDescriptions'][0]['PrimaryFolder'].split('.')[1] + '\n') #print province
    
    file.close()
    print('Script Successfully Completed!')

getData()
