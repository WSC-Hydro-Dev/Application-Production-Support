import os
import xml.etree.ElementTree as ET
import requests
import datetime
from datetime import datetime as dt
import time
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math
import unicodedata

# Global variables needed by CDP aquarius code
AQ_time = '%Y-%m-%dT%H:%M:%S'
AQ_base_url = 'https://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2/'
server_pub = "https://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"

def getDataNG(stationId, paras, s):
    start_time_getDataNG = time.time()
    para, date_from, corrected = paras
    '''Gets station data from AQ NG, and returns it as a Python list'''
    #Get unique ID
    parameter = para.split(".")[0]
    url = (AQ_base_url+'GetTimeSeriesDescriptionList?LocationIdentifier='+stationId+'&Parameter='+parameter)
    response = s.get(url)

    data = json.loads(response.text)
    uniqueID = ''
    for i in data['TimeSeriesDescriptions']:
        if i['Identifier'] == para+'@'+stationId:
            uniqueID = i['UniqueId']
            break

    #data_list = [['Time','Value']]
    data_list = []
    if uniqueID != '':
        #Get station data
        if corrected:
            url = (AQ_base_url+'GetTimeSeriesData?TimeSeriesUniqueIds='+uniqueID+
                    '&QueryFrom='+date_from.strftime('%Y-%m-%d'))
            response = s.get(url)

            today_date = datetime.date.today()
            prev_year = today_date+datetime.timedelta(-30)

            if date_from == prev_year:
                data = json.loads(response.text)['Points'][::36]
            else:
                data = json.loads(response.text)['Points'][::4]

            for i in data:
                try:
                    data_list.append([i['Timestamp'], i['NumericValue1']])
                except KeyError:
                    pass
        else: #raw data
            url = (AQ_base_url+'GetTimeSeriesRawData?TimeSeriesUniqueId='+uniqueID+
                    '&QueryFrom='+date_from.strftime('%Y-%m-%d'))
            response = s.get(url)

            data = json.loads(response.text)['Points'][::4]
            for i in data:
                try:
                    data_list.append([i['Timestamp'], i['Value']['Numeric']])
                except KeyError:
                    pass

    # data_process() is used to clean up the raw AQ data
    # while modifyDataNG() is used to convert the data into a form that's easier to use
    print("get data NG time:")
    print("--- %s seconds ---" % (time.time() - start_time_getDataNG))
    return modifyDataNG(data_process(list(data_list)))


# Ethan Johnson's CDP code
####################################################
###             Clean up raw AQ data             ###
####################################################
def data_process(in_list):
    j = 0
    while j <= len(in_list):
        try:  # Either format data to float, or remove if empty so there aren't issues plotting
            if in_list[j][1] == '' or in_list == []:
                del in_list[j]
                j -= 1
            else:
                in_list[j][1] = s_rnd(float(in_list[j][1]))
        except:
            pass
        try:  # Format date
            in_list[j][0] = dt.strptime(in_list[j][0][:19], AQ_time)
        except:
            pass

        j += 1
    return in_list


# Ethan Johnson's CDP code
####################################################
### Round to 4 sig figs, to save temp file space ###
####################################################
def s_rnd(num):
    sig_figs = 4
    try:
        return round(num, int(sig_figs - math.ceil(math.log10(abs(num)))))
    except Exception as e:
        # print(e)
        return num


# Function for adding a zero to the beginning of the string representation of days and months
# If the day or the month is less than 10, then add a 0 to the day or the month as a string
# and return it, otherwise just return the day or the month as a string
def fixDate(dayOrMonth):
    if dayOrMonth < 10:
        return '0' + str(dayOrMonth)
    return str(dayOrMonth)


def modifyDataNG(list_of_data):
    # Create arrays to hold the separated times and values
    times = []
    values = []
    # Iterate over every value in the list of data
    for i in range(0, len(list_of_data)):
        # Grab the time and spit it into year, month, day, hour, and minute, and call fixDate() for the month, day, hour, and minute
        # Then create the string representing the time in the more usable format
        newTime = str(list_of_data[i][0].year) + '-' + fixDate(list_of_data[i][0].month) + '-' + fixDate(
            list_of_data[i][0].day) + 'T' + fixDate(list_of_data[i][0].hour) + ':' + fixDate(list_of_data[i][0].minute)
        # Append the time and corresponding value to the array
        times.append(newTime)
        values.append(list_of_data[i][1])
    # Create an array to hold the times and values and append them to the array
    array_of_all_data = []
    array_of_all_data.append(times)
    array_of_all_data.append(values)
    # Return the array
    return array_of_all_data


# Ethan Johnson's CDP code (modified)
####################################################
###             Get station visit info           ###
####################################################
def getStationVisitInfo(stationId, s):
    start_time_v = time.time()
    # Get field visit data
    url = (AQ_base_url + 'GetFieldVisitDataByLocation?' +
           'LocationIdentifier=' + stationId)
    response = s.get(url)
    fv = json.loads(response.text)
    # field_visit_discharge = [['Time', 'Q', 'HG']]
    # field_visit_stage = [['Time','HG']]
    # field_visit_stage = ['Time']
    field_visit_discharge = []
    field_visit_stage = []
    for i in fv['FieldVisitData']:
        try:  # see if there's discharge data
            Q_sum = i['DischargeActivities'][0]['DischargeSummary']

            hg = Q_sum['MeanGageHeight']['Numeric']
            qr = Q_sum['Discharge']['Numeric']
            startTime = Q_sum['MeasurementTime']
            startTime = dt.strptime(startTime[:19], AQ_time)
            # The date is changed to a string in the form of "yyyy-mm-dd" to make it more easily comparable with other dates
            fixed_date = str(startTime.year) + '-' + fixDate(startTime.month) + '-' + fixDate(startTime.day)
            # field_visit_discharge.append(fixed_date)
            field_visit_discharge.append([fixed_date, qr, hg])

        except KeyError as e:
            # print(e)
            # print('trying to get field visit data')
            pass
        try:  # see if there's stage data
            for j in i['InspectionActivity']['Readings']:
                if j['Parameter'] == 'Stage' and j['Publish']:
                    # val = j['Value']['Numeric']
                    visit_datetime = j['Time']
                    visitDateDateTime = dt.strptime(visit_datetime[:19], AQ_time)
                    # The date is changed to a string in the form of "yyyy-mm-dd" to make it more easily comparable with other dates
                    fixed_date = str(visitDateDateTime.year) + '-' + fixDate(visitDateDateTime.month) + '-' + fixDate(
                        visitDateDateTime.day)
                    # field_visit_stage.append([visitDateDateTime, val])
                    field_visit_stage.append(fixed_date)

        except KeyError as e:
            pass

    # Add both arrays to a single array
    array_for_both = []
    array_for_both.append(field_visit_discharge)
    array_for_both.append(field_visit_stage)

    print("get Visit Time:")
    print("--- %s seconds ---" % (time.time() - start_time_v))
    return array_for_both


# Ethan Johnson's CDP code (modified)
####################################################
###             Get rating curve info            ###
####################################################
def getRatingCurveInfo(stationId, s):
    start_time_rc = time.time()

    url = (AQ_base_url + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + stationId)
    response = s.get(url)
    data = json.loads(response.text)
    dischargeID = ''  # dischargeID is also useful to know whether to try and get a rating curve
    for i in data['TimeSeriesDescriptions']:
        if i['Identifier'] == 'Discharge.Working@' + stationId:
            dischargeID = i['UniqueId']

    # Arrays to hold the rating curve data
    HG_curve = []
    Q_curve = []
    HG_curve_shift = []
    Q_curve_shift = []
    curve_shift_val = []
    rating_point_HG = []
    rating_point_Q = []
    date_of_applicability = []

    if dischargeID != '':
        # Get rating curve data
        url = (AQ_base_url + 'GetRatingModelDescriptionList?' +
               'LocationIdentifier=' + stationId)
        response = s.get(url)
        rating_info = json.loads(response.text)
        rating_Id = ''
        # rating_Id should always be "Stage-Discharge.Rating Curve@station_Id",
        # I think, but getting it manually just in case
        for i in rating_info['RatingModelDescriptions']:
            if i['Label'] == 'Rating Curve':
                rating_Id = i['Identifier']
        url = (AQ_base_url + 'GetEffectiveRatingCurve?' +
               'RatingModelIdentifier=' + rating_Id)
        response = s.get(url)
        curve_data = json.loads(response.text)
        # There's at least one station at the time of testing that has stage, discharge,
        # and a rating curve, but the rating curve can't be accessed via the AQ API.
        # This try catches that, without wrapping the whole block to catch a KeyError,
        # to make any future debugging a bit easier
        try:
            curve_data['ExpandedRatingCurve']
            continue_bool = True
        except KeyError:
            continue_bool = False

        if continue_bool:
            # curve_list = [['HG','Q']]
            for i in curve_data['ExpandedRatingCurve']['BaseRatingTable']:
                # curve_list.append([i['InputValue'],i['OutputValue']])
                HG_curve.append(i['InputValue'])
                Q_curve.append(i['OutputValue'])

            # Get shifted curve
            try:
                # curve_list = [['HG','Q']]
                for i in curve_data['ExpandedRatingCurve']['AdjustedRatingTable']:
                    # curve_list.append([i['InputValue'],i['OutputValue']])
                    HG_curve_shift.append(i['InputValue'])
                    Q_curve_shift.append(i['OutputValue'])

                # Can only handle one shift value
                shift_val = curve_data['ExpandedRatingCurve']['Shifts'][0]['ShiftPoints'][0]['Shift']
                curve_shift_val.append(shift_val)
            except:
                pass

            # Get rating points
            curve_number = curve_data['ExpandedRatingCurve']['Id']
            url = (AQ_base_url + 'GetRatingCurveList?' +
                   'RatingModelIdentifier=' + rating_Id)
            response = s.get(url)
            all_curves = json.loads(response.text)
            # rating_point_list = [['HG','Q']]
            for i in all_curves['RatingCurves']:
                if i['Id'] == curve_number:
                    for j in i['BaseRatingTable']:
                        # rating_point_list.append([j['InputValue'],j['OutputValue']])
                        rating_point_HG.append(j['InputValue'])
                        rating_point_Q.append(j['OutputValue'])

            # Get most recent rating curve period of applicability
            appFromDate = ''
            for i in curve_data['ExpandedRatingCurve']['PeriodsOfApplicability']:
                appFromDate = i['StartTime']
            # appFromDate = [dt.strptime(appFromDate[:19],AQ_time)]
            appFromDate = dt.strptime(appFromDate[:19], AQ_time)
            # The date is changed to a string in the form of "yyyy-mm-dd" to make it more easily comparable with other dates
            fixed_date = str(appFromDate.year) + '-' + fixDate(appFromDate.month) + '-' + fixDate(appFromDate.day)
            date_of_applicability.append(fixed_date)

    # Creating array to hold all the rating curve data
    array_of_all_rating_curve_data = []

    # Combining the rating curve data into a single array and appending it to the large array
    array_rating_curve = []
    array_rating_curve.append(HG_curve)
    array_rating_curve.append(Q_curve)
    array_of_all_rating_curve_data.append(array_rating_curve)

    # Combining the rating curve shift data into a single array and appending it to the large array
    array_rating_curve_shift = []
    array_rating_curve_shift.append(HG_curve_shift)
    array_rating_curve_shift.append(Q_curve_shift)
    array_of_all_rating_curve_data.append(array_rating_curve_shift)

    # Appending the shift value to the large array
    array_of_all_rating_curve_data.append(curve_shift_val)

    # Appending the point list to the large array
    rating_point_list = []
    rating_point_list.append(rating_point_HG)
    rating_point_list.append(rating_point_Q)
    array_of_all_rating_curve_data.append(rating_point_list)

    # Appending the date of applicability to the large array
    array_of_all_rating_curve_data.append(date_of_applicability)

    print("get RC Time:")
    print("--- %s seconds ---" % (time.time() - start_time_rc))
    return array_of_all_rating_curve_data


def getCorrection(stationId, s):
    #Get recent corrections
    url = (AQ_base_url+'GetTimeSeriesDescriptionList?LocationIdentifier='+stationId)
    response = s.get(url)
    data = json.loads(response.text)
    stageID = '' #UniqueIDs are needed for the corrections
    dischargeID = '' #dischargeID is also useful to know whether to try and get a rating curve
    for i in data['TimeSeriesDescriptions']:
        if i['Identifier'] == 'Discharge.Working@'+stationId:
            dischargeID = i['UniqueId']
        elif i['Identifier'] == 'Stage.Working@'+stationId:
            stageID = i['UniqueId']
    correction_list = []
    stationOff = False
    if stageID != '':
        url = (AQ_base_url+'GetCorrectionList?TimeSeriesUniqueId='+stageID)
        response = s.get(url)
        data = json.loads(response.text)
        for i in data['Corrections']:
            cor_type = i['Type']
            cor_start = dt.strptime(i['StartTime'][:19],AQ_time)
            cor_end = dt.strptime(i['EndTime'][:19],AQ_time)
            cor_start_date = str(cor_start.year) + '-' + fixDate(cor_start.month) + '-' + fixDate(cor_start.day) + 'T' + str(cor_start.hour) + ':' + str(cor_start.minute)
            cor_end_date = str(cor_end.year) + '-' + fixDate(cor_end.month) + '-' + fixDate(cor_end.day) + 'T' + str(cor_end.hour) + ':' + str(cor_end.minute)
            if cor_end.year == 9999:
                #for ongoing corrections, convert to future
                #date that pandas/numpy can actually handle
                cor_end = datetime.datetime(2262,1,1)
            cor_applied = dt.strptime(i['AppliedTimeUtc'][:19],AQ_time)
            fixed_date = str(cor_applied.year) + '-' + fixDate(cor_applied.month) + '-' + fixDate(cor_applied.day)

            cor_comment = i['Comment']
            cor_user = i['User']
            correction_list.append([fixed_date,cor_type,'HG',cor_comment])
            #Check if station is active
            if cor_user != "Migration" and cor_type == "DeleteRegion":
                if cor_start <= dt.today() <= cor_end:
                    stationOff = True
    if dischargeID != '':
        url = (AQ_base_url+'GetCorrectionList?TimeSeriesUniqueId='+dischargeID)
        response = s.get(url)
        data = json.loads(response.text)
        for i in data['Corrections']:
            cor_type = i['Type']
            cor_start = dt.strptime(i['StartTime'][:19],AQ_time)
            cor_end = dt.strptime(i['EndTime'][:19],AQ_time)
            cor_start_date = str(cor_start.year) + '-' + fixDate(cor_start.month) + '-' + fixDate(
                cor_start.day) + 'T' + str(cor_start.hour) + ':' + str(cor_start.minute)
            cor_end_date = str(cor_end.year) + '-' + fixDate(cor_end.month) + '-' + fixDate(cor_end.day) + 'T' + str(
                cor_end.hour) + ':' + str(cor_end.minute)
            if cor_end.year == 9999:
                #for ongoing corrections, convert to future
                #date that pandas/numpy can actually handle
                cor_end = datetime.datetime(2262,1,1)
            cor_applied = dt.strptime(i['AppliedTimeUtc'][:19],AQ_time)
            fixed_date = str(cor_applied.year) + '-' + fixDate(cor_applied.month) + '-' + fixDate(cor_applied.day)
            cor_comment = i['Comment']
            cor_user = i['User']
            correction_list.append([fixed_date,cor_type,'Q',cor_comment])
        print("here")

    applied = []
    type = []
    corr_data = []
    comment = []
    formatted_corr_list = []
    correction_list.sort(reverse=True)
    for i in range(len(correction_list)):
        applied.append(correction_list[i][0])
        type.append(correction_list[i][1])
        corr_data.append(correction_list[i][2])
        comment.append(correction_list[i][3])

    formatted_corr_list.append(applied)
    formatted_corr_list.append(type)
    formatted_corr_list.append(corr_data)
    formatted_corr_list.append(comment)

    return formatted_corr_list


def getTSUniqueID(stationID, s):
    for station in stationID:
        stnUrl = server_pub + 'GetTimeSeriesDescriptionList?LocationIdentifier=' + station + '&Parameter=Discharge'
        req = requests.get(stnUrl)
        data = json.loads(req.text)
        uniqueID = ''
        for i in data['TimeSeriesDescriptions']:
            if i['Identifier'] == 'Discharge.Working@' + station:
                uniqueID = i['UniqueId']
                break
    return uniqueID


def checkChangeSince(stationID, parameter, s):
    currentTime = dt.now()
    print(currentTime.minute)
    nextTokenTime = str(currentTime - datetime.timedelta(minutes=currentTime.minute))[:19]
    print(nextTokenTime)
    changeUrl = server_pub + 'GetTimeSeriesUniqueIdList?ChangesSinceToken='+ nextTokenTime + '&ChangeEventType=Data&LocationIdentifier=' + stationID + '&Parameter=' + parameter
    req = s.get(changeUrl)
    response = json.loads(req.text)
    print(response)

def getDataCSV(stationID, path, parameter, s):
    start_time_getDataCSV = time.time()

    uniqueId = checkChangeSince(stationID, parameter, s)


    data_list = []
    if os.path.isfile(path):
        exists = True
        print("File exist")
    else:
        print("File not exist")
        exists = False

    if exists:
        with open(path) as fp:
            line = fp.readline()
            while line:
                reading = line.split(",")
                date = reading[0][:19]
                data = reading[1][:5]
                data_list.append([date, data])
                line = fp.readline()

    print("get data CSV time:")
    print("--- %s seconds ---" % (time.time() - start_time_getDataCSV))
    return modifyDataNG(data_process(list(data_list)))



def getAquariusData(stationID):

    start_time_l = time.time()
    # Aquarius username and password
    loginID = 'USERNAME'
    password = 'PASSWORD'

    s = requests.Session()
    url = AQ_base_url + 'session'
    s.post(url, data={'Username': loginID, 'EncryptedPassword': password})

    # Get the cutoff dates used when calling getDataNG()
    today_date = datetime.date.today()
    prev_8_day = today_date + datetime.timedelta(-8)
    prev_two_weeks = today_date + datetime.timedelta(-14)
    prev_30_day = today_date + datetime.timedelta(-30)

    print("get Login Time:")
    print("--- %s seconds ---" % (time.time() - start_time_l))

    # Getting the 30-day discharge and stage data
    array0 = getDataNG(stationID, ('Discharge.Working', prev_30_day, True), s)
    array1 = getDataNG(stationID, ('Stage.Working', prev_30_day, True), s)

    arrayT1 = getDataCSV(stationID, 'C:\\_dev\\outputStnData.csv', 'Stage', s)
    arrayT2 = getDataCSV(stationID, 'C:\\_dev\\outputStnDataD.csv', 'Discharge', s)

    # Getting the station visit data
    array2 = getStationVisitInfo(stationID, s)

    # Getting the raw and corrected 8-day discharge data
    array3 = getDataNG(stationID, ('Discharge.Working', prev_8_day, True), s)
    array4 = getDataNG(stationID, ('Stage.Working', prev_8_day, True), s)
    array5 = getDataNG(stationID, ('Discharge.Working', prev_8_day, False), s)
    array6 = getDataNG(stationID, ('Stage.Working', prev_8_day, False), s)

    # Getting the two weeks of telemetry data
    array7 = getDataNG(stationID, ('Voltage.Telemetry', prev_two_weeks, True), s)
    array8 = getDataNG(stationID, ('Tank Pressure.Telemetry', prev_two_weeks, True), s)
    array9 = getDataNG(stationID, ('Signal Strength.Telemetry', prev_two_weeks, True), s)
    array10 = getDataNG(stationID, ('Forward Power.Telemetry', prev_two_weeks, True), s)
    array11 = getDataNG(stationID, ('Reflective Power.Telemetry', prev_two_weeks, True), s)

    # Getting the rating curve data
    array12 = getRatingCurveInfo(stationID, s)
    array13 = getCorrection(stationID, s)[:6]

    # Deleting the Aquarius session
    s.delete(url)

    # Add all the data to a single array
    bigArray = []
    bigArray.append(array0)
    bigArray.append(array1)
    bigArray.append(array2)
    bigArray.append(array3)
    bigArray.append(array4)
    bigArray.append(array5)
    bigArray.append(array6)
    bigArray.append(array7)
    bigArray.append(array8)
    bigArray.append(array9)
    bigArray.append(array10)
    bigArray.append(array11)
    bigArray.append(array12)
    bigArray.append(array13)

    # Convert the single array to a json string and return it
    jsonStringOld = json.dumps(bigArray)

    print("DONE")
    # return jsonStringOld



#######################################################
# Small helper functions used in routes.py and forms.py
#######################################################


# Get today's date
def getToday():
    return dt.today().date()


# Get the date 90 days (3 months) ago
def getNintyDaysAgo():
    return dt.today().date() + datetime.timedelta(-90)


# Function for checking if a given date is in the past
def checkDate(nextDate):

    # Get today's date
    today = getToday()
    # If nextDate is not null and is in the past, then return true
    # Otherwise return false
    if (nextDate != None):
        if (nextDate < today):
            return True
    return False


def main():
    print("Start!!")
    getAquariusData("05AA004")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total time:")
    print("--- %s seconds ---" % (time.time() - start_time))

