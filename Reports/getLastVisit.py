import requests
import json
import re
from datetime import datetime as dt
from dateutil.parser import parse
'''
stations = ['07DD003','07DD007','07DD011','07KC001','07KC005','07KF002','07KF003','07KF015','07MD001','07NA001','07NA007','07NA008',
            '07NB001','08BB005','09ED001','09AA001','09AA006','09AA013','09AE003','10BE001','10BE004','10BE007','10BE009','10BE013',
            '10DA001','10LA002','10LB005','10LB006','10LC002','10LC003','10LC007','10LC012','10LC013','10LC014','10LC015','10LC017',
            '10LC019','10LC020','10LC021','10MC002','10MC003','10MC007','10MC008','10MC010','10MC011','10MC022','10MC023','10NC001',
            '10ND002','10ND004','10OB001','10TA001','30NT002','06JA001','06JB001','06KB003','07OB001','07OB002','07OB008','07PA001',
            '07QC007','07QD002','07QD007','07RB001','07RD001','07SA002','07SA004','07SA008','07SB001','07SB002','07SB003','07SB010',
            '07SB012','07SB013','07SB014','07SB015','07SB017','07SB020','07SC001','07SC002','07SC004','07SC005','07TA001','07UC001',
            '10EA003','10EB001','10EC003','10ED001','10ED002','10ED003','10ED007','10ED009','10ED010','10FA002','10FB001','10FB005',
            '10FB006','10GA001','10GB006','10GC001','10GC003','10GD001','10GD002','10HA004','10HB005','10HC008','10JA002','10JA003',
            '10JB001','10JC003','10JD002','10JE002','10KA001','10KA006','10KA007','10KA008','10KA009','10KB001','10KC001','10KD001',
            '10KD009','10LB004','10LB007','10LD001','10LD004','10NB001','10PA001','10PA002','10PB001','10PB003','10ZZ099','30NT001',
            '30NT003','06HB002','06JC002','06KC003','06LA001','06LA003','06LC001','06MA006','06OA007','10PC004','10PC005','10QA001',
            '10QC001','10QC003','10QD001','10RA001','10RA002','10RC001','10RC002','10TF001','10UH001','10UH002','10UH012','10UH013',
            '10UH015','10VC002','10VK001','10MD001','10MD002','10MD003','08AA003','08AA005','08AA007','08AA008','08AA009','08AA010',
            '08AA011','08AA012','08AB001','08AC001','08AC002','09AA004','09AA012','09AA017','09AB001','09AB004','09AB010','09AC001',
            '09AC007','09AD002','09AE002','09AE006','09AG001','09AH001','09AH003','09AH004','09AH005','09BA001','09BB001','09BC001',
            '09BC002','09BC004','09CA001','09CA002','09CA004','09CA006','09CB001','09CD001','09DA001','09DB001','09DC005','09DC006',
            '09DD003','09DD004','09EA003','09EA004','09EA005','09EA006','09EB001','09EB003','09EB004','09FA001','09FB002','09FB003',
            '09FC001','09FD002','09FD003','10AA001','10AA004','10AA005','10AA006','10AB001','10AD002','10BD001','10DB001','10MA001',
            '10MA002','10MA003','10MB004']
'''
stations = ['02BB101','02BB102','02BBX01','02BD002','02BE002','02CA008','02EB004','02EB006','02EB008','02EB011','02EB012','02EB014','02EB015','02EB017',
            '02EB018','02EB019','02EB020','02EB021','02EB023','02EC002','02EC003','02EC008','02EC009','02EC010','02EC011','02EC014','02EC018','02EC019',
            '02EC020','02EC021','02EC022','02ED003','02ED007','02ED012','02ED013','02ED014','02ED015','02ED017','02ED024','02ED026','02ED027','02ED029',
            '02ED030','02ED031','02ED032','02ED033','02ED100','02ED101','02ED102','02FA001','02FA002','02FA003','02FA004','02FB007','02FB009','02FB010',
            '02FB012','02FB013','02FB014','02FC001','02FC002','02FC011','02FC012','02FC015','02FC016','02FC017','02FC020','02FC021','02FD001','02FD002',
            '02FD003','02FE002','02FE003','02FE005','02FE007','02FE008','02FE009','02FE010','02FE011','02FE012','02FE013','02FE014','02FE015','02FE016',
            '02FE017','02FE018','02FF002','02FF004','02FF007','02FF008','02FF009','02FF010','02FF011','02FF012','02FF013','02FF014','02FF015','02FF016',
            '02GA003','02GA005','02GA006','02GA010','02GA014','02GA015','02GA016','02GA018','02GA023','02GA024','02GA028','02GA029','02GA030','02GA031',
            '02GA034','02GA038','02GA039','02GA040','02GA041','02GA042','02GA043','02GA044','02GA045','02GA046','02GA047','02GA048','02GA049','02GA050',
            '02GB001','02GB006','02GB007','02GB008','02GB010','02GC002','02GC006','02GC007','02GC008','02GC010','02GC011','02GC014','02GC017','02GC018',
            '02GC021','02GC022','02GC026','02GC027','02GC028','02GC029','02GC030','02GC031','02GC036','02GC037','02GC038','02GD001','02GD003','02GD004',
            '02GD005','02GD008','02GD009','02GD010','02GD011','02GD014','02GD015','02GD016','02GD018','02GD019','02GD021','02GD022','02GD026','02GD027',
            '02GD028','02GE002','02GE003','02GE004','02GE005','02GE006','02GE007','02GE008','02GE009','02GEQ03','02GF002','02GG002','02GG003','02GG005',
            '02GG006','02GG008','02GG009','02GG010','02GG011','02GG013','02GGQ03','02GGQ04','02GGQ05','02GH002','02GH003','02GH005','02GH008','02GH009',
            '02GH010','02GH011','02GH016','02HA003','02HA006','02HA007','02HA013','02HA014','02HA017','02HA018','02HA019','02HA020','02HA024','02HA030',
            '02HA031','02HA032','02HAQ13','02HAQ19','02HB001','02HB004','02HB005','02HB007','02HB008','02HB011','02HB012','02HB013','02HB015','02HB017',
            '02HB018','02HB020','02HB021','02HB022','02HB023','02HB024','02HB025','02HB027','02HB028','02HB029','02HB030','02HB031','02HB032','02HB033',
            '02HC003','02HC005','02HC009','02HC013','02HC017','02HC018','02HC019','02HC022','02HC023','02HC024','02HC025','02HC027','02HC028','02HC030',
            '02HC031','02HC032','02HC033','02HC038','02HC047','02HC048','02HC049','02HC051','02HC053','02HC054','02HC055','02HC056','02HC058','02HC059',
            '02HCX18','02HCX56','02HD003','02HD004','02HD006','02HD008','02HD009','02HD012','02HD013','02HD020','02HD021','02HD023','02HD024','02HF002',
            '02HF003','02HG001','02HG002','02HG003','02HH003','02HH005','02HJ001','02HJ003','02HJ006','02HJ007','02HJ009','02HJ010','02HJ011','02MAQ30',
            '05PB009','05QD016','30ON001','99ZZ012','02BA003','02BC006','02BC008','02BD004','02BD005','02BD006','02BDX06','02BF001','02BF002','02BF004',
            '02BF010','02BF011','02BF014','02CA002','02CA003','02CA005','02CA006','02CA007','02CB003','02CC005','02CC008','02CC010','02CD001','02CD006',
            '02CE002','02CE007','02CF005','02CF007','02CF008','02CF010','02CF011','02CF012','02CF013','02CF014','02CG002','02CG003','02CG005','02CH001',
            '02CH002','02DB005','02DB007','02DC004','02DC012','02DC013','02DD006','02DD010','02DD012','02DD013','02DD014','02DD015','02DD016','02DD017',
            '02DD020','02DD021','02DD022','02DD023','02DD024','02DD025','02DD026','02DDX01','02DDX02','02DDX03','02EA005','02EA010','02EA011','02EA014',
            '02EA015','02EA016','02EA018','02EA019','02EA020','02EA021','02EB013','02EB016','02EB022','02JC008','02JD013','02JD014','02JE011','02JE013',
            '02JE027','02JE028','02JE032','02KA015','02KB001','02KC015','02KC018','04DC002','04EA001','04FB001','04FC001','04FC002','04FC003','04GD001',
            '04HA001','04HA002','04HA003','04JC002','04JD005','04JF001','04JG001','04KA001','04LA002','04LA003','04LA004','04LA005','04LA006','04LB002',
            '04LC002','04LC003','04LD001','04LE002','04LF001','04LG004','04LGX01','04LJ001','04LK001','04LM001','04MB002','04MB005','04MD004','04MD005',
            '04ME003','04MF001','30ON003','99ZZ101','99ZZ102','99ZZ206','02HD010','02HD015','02HD018','02HD019','02HD022','02HE002','02HE004','02HK003',
            '02HK005','02HK006','02HK007','02HK008','02HK009','02HK010','02HK011','02HK015','02HK016','02HK017','02HL001','02HL003','02HL004','02HL005',
            '02HL007','02HL008','02HM002','02HM003','02HM004','02HM005','02HM006','02HM007','02HM008','02HM009','02HM010','02HM011','02KC009','02KD002',
            '02KD004','02KF001','02KF005','02KF006','02KF010','02KF011','02KF012','02KF013','02KF015','02KF016','02KF017','02KF018','02KF019','02KF020',
            '02KFX95','02KFX96','02KFX97','02KFX98','02KFX99','02LA004','02LA006','02LA007','02LA024','02LA027','02LA028','02LB005','02LB006','02LB007',
            '02LB008','02LB009','02LB013','02LB017','02LB018','02LB020','02LB022','02LB031','02LB032','02LB036','02LBX06','02MA001','02MB006','02MB007',
            '02MB008','02MB010','02MC001','02MC022','02MC023','02MC026','02MC027','02MC028','02MC030','02MC036','02MC037','30ON002','30ON005','99ZZG02',
            '99ZZG03','02AB006','02AB008','02AB014','02AB017','02AB018','02AB019','02AB020','02AB021','02AB022','02AB023','02AB024','02AB025','02AB026',
            '02AB027','02ABX14','02AC001','02AC002','02AD010','02AD012','02AE001','02BA004','02BA005','02BA006','02BB003','02BB004','02BC007','04CA002',
            '04CA003','04CA004','04CA005','04CB001','04DA001','04DA002','04DB001','04DC001','04FA001','04FA002','04FA003','04GA002','04GA003','04GB004',
            '04GB005','04GC002','04JD006','05PA006','05PA012','05PA013','05PB014','05PB018','05PB024','05PC018','05PC019','05PE020','05QA002','05QA004',
            '05QA006','05QB001','05QB002','30ON004','05PB007','05PB023','05PC021','05PC022','05PC023','05PC024','05PC025','05PD008','05PD011','05PD029',
            '05PE001','05PE006','05PE009','05PE011','05PE012','05PE014','05PE028','05PE029','05PE030','05PE031','05PF051','05QB003','05QC001','05QC004',
            '05QC005','05QC006','05QC007','05QD006','05QD029','05QE008','05QE009','05QE012','05QE015','05RC001']
#stations.append('01DC007')
Server = "http://wsc.aquaticinformatics.net/AQUARIUS/publish/v2/"
server_pro = "https://wsc.aquaticinformatics.net/AQUARIUS/Provisioning/v1/"
reportYear = parse("2020/01/01")
reportEndYear = parse("2019/01/01")

# Login
userName = "USERNAME"
password = "PASSWORD"
s = requests.Session()
data = '{"Username": "' + userName + '", "EncryptedPassword": "' + password + '", "Locale": ""}'
url = server_pro + 'session'
s.get(url)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
r = s.post(url, data=data, headers=headers)
token = r.text
print token

# for each station
fieldVisitInfoList = []
for station in stations:
    # load the all field visit for one station into json file
    print station

    exists = False
    try:
        req = requests.get(Server + 'GetFieldVisitDataByLocation?LocationIdentifier=' + station + '&token=' + token)
        fieldDescriptions = req.json()['FieldVisitData']
        exists = True
    except:
        print "Failed to load Field Visit Data for Station:" + station
        continue

    try:
        req = requests.get(Server + 'GetLocationData?LocationIdentifier='+station+'&token='+ token)
        locationName = req.json()['LocationName']
    except:
        print "Failed to get station name for station:" + station
        continue

    if exists and len(fieldDescriptions) != 0:
        # final list
        # for each field visit
        fieldVisitData = fieldDescriptions[0]
        fieldId = fieldVisitData['Identifier']
        startTime = fieldVisitData['StartTime']
        start = fieldVisitData['StartTime'].replace('-', '/')
        fieldVisitDate = parse(start[0:10])

        print fieldVisitDate

        hasReadings = False
        hasStage = False
        hasDischarge = False
        hasMGH = False
        # look for reading for the field visit
        try:
            fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
            hasReadings = True
        except:
             pass

        if hasReadings:
            if len(fieldVisitReadings) != 0:

                fieldDataStagelist = []
                fieldDateDischargelist = []
                print "hasReading"
                # Stage
                try:
                    # check if MGH exists
                    fieldVisitStage = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeanGageHeight']['Numeric']
                    hasMGH = True
                except:
                    pass

                # if stage exists then append info to the list
                if hasMGH:
                    locationId = station
                    date = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][0:10]
                    activity = "Stage"
                    meanTime = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][11:19]
                    tz = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][-6:]
                    discharge = ''
                    RcNo = ''
                    shift = ''
                    controlCond = ''
                    try:
                        activityRemark = fieldVisitData['Remarks']
                    except:
                        activityRemark = ''
                    locationRemark = ''
                    activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                    fieldDataStagelist.append(str(locationId) + ',')
                    fieldDataStagelist.append(str(locationName) + ',')
                    fieldDataStagelist.append(str(date) + ',')
                    fieldDataStagelist.append(str(activity) + ',')
                    fieldDataStagelist.append(str(meanTime) + ',')
                    fieldDataStagelist.append(str(tz) + ',')
                    fieldDataStagelist.append(str(fieldVisitStage) + ',')
                    fieldDataStagelist.append(str(discharge) + ',')
                    fieldDataStagelist.append(str(RcNo) + ',')
                    fieldDataStagelist.append(str(shift) + ',')
                    fieldDataStagelist.append(str(controlCond) + ',')
                    fieldDataStagelist.append(str(activityRemark).replace("," , "").replace("\n", " ").replace("\r", " ").replace("==Aggregated measurement activity remarks:  ", "") + ',')
                    fieldDataStagelist.append(str(locationRemark) + ',')
                    fieldDataStagelist.append(' ' + '\n')
                    fieldVisitInfoList.append(fieldDataStagelist)
                    print "Add MGH"
                else:
                    try:
                        fieldVisitReadings = fieldVisitData['InspectionActivity']['Readings']
                        hasStage = True
                    except:
                        pass

                    if hasStage:
                        fieldVisitStage = ''
                        readingComments = ''
                        readingTime = ''
                        for i in fieldVisitReadings:
                            if i['Parameter'] == 'Stage' and i['MonitoringMethod'] != 'Logger':
                                try:
                                    fieldVisitStage = i['Value']['Numeric']
                                    readingTime = i['Time']
                                except:
                                    fieldVisitStage = ""
                                    readingTime = ""
                                try:
                                    readingComments = i['Comments']
                                except:
                                    readingComments = ""
                        stage1 = fieldVisitStage
                        comments = readingComments
                        if fieldVisitStage == "":
                            activity = "No Stage or Discharge Measurement"
                        else:
                            activity = "Stage"

                        locationId = station
                        if readingTime != '':
                            date = readingTime[0:10]
                            meanTime = readingTime[11:19]
                            tz = readingTime[-6:]
                        else:
                            date = startTime[0:10]
                            meanTime = startTime[11:19]
                            tz = startTime[-6:]
                        discharge = ''
                        RcNo = ''
                        shift = ''
                        controlCond = ''
                        try:
                            activityRemark = fieldVisitData['Remarks']
                        except:
                            activityRemark = ''
                        locationRemark = ''
                        activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                        fieldDataStagelist.append(str(locationId) + ',')
                        fieldDataStagelist.append(str(locationName) + ',')
                        fieldDataStagelist.append(str(date) + ',')
                        fieldDataStagelist.append(str(activity) + ',')
                        fieldDataStagelist.append(str(meanTime) + ',')
                        fieldDataStagelist.append(str(tz) + ',')
                        fieldDataStagelist.append(str(stage1) + ',')
                        fieldDataStagelist.append(str(discharge) + ',')
                        fieldDataStagelist.append(str(RcNo) + ',')
                        fieldDataStagelist.append(str(shift) + ',')
                        fieldDataStagelist.append(str(controlCond) + ',')
                        fieldDataStagelist.append(str(activityRemark).replace("," , "").replace("\n", " ").replace("\r", " ").replace("==Aggregated measurement activity remarks:  ", "") + ',')
                        fieldDataStagelist.append(str(locationRemark) + ',')
                        fieldDataStagelist.append(' ' + '\n')
                        fieldVisitInfoList.append(fieldDataStagelist)
                        print "Add Stage"


                # discharge
                try:
                    # check if discharge exists
                    fieldVisitDischarge = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['Discharge']['Numeric']
                    hasDischarge = True
                except:
                    pass

                if hasDischarge:
                    locationId = station
                    date = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][0:10]
                    activity = "Discharge"
                    meanTime = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][11:19]
                    tz = fieldVisitData['DischargeActivities'][0]['DischargeSummary']['MeasurementTime'][-6:]
                    if hasMGH:
                        stage = fieldVisitStage
                    else:
                        stage = stage1
                    formattedDischarge = []
                    formattedDischarge.append(fieldVisitDischarge)

                    # get shift
                    try:
                        shiftreq = requests.get(Server+"GetRatingModelInputValues?RatingModelIdentifier=""Stage-Discharge.Rating Curve@"+station+"&OutputValues="+str(fieldVisitDischarge)+"&EffectiveTime="+date+"&token="+token)
                        #shiftreq = requests.get(Server+"GetRatingModelInputValues?RatingModelIdentifier=Stage-Discharge.Rating%20Curve%4001DC007&OutputValues=80.7&EffectiveTime=2019-09-10&token="+token)
                        unshiftedStage = shiftreq.json()['InputValues'][0]
                    except:
                        unshiftedStage = None
                        print "error while getting unshifted value"
                    print stage
                    if unshiftedStage != None and stage != '':
                        shift  = stage - unshiftedStage
                    else:
                        shift = 'N/A'
                    # get rc no
                    try:
                        rcreq = requests.get(Server+"GetRatingCurveList?RatingModelIdentifier=""Stage-Discharge.Rating Curve@"+station+"&QueryFrom="+date+"&QueryTo="+date+"&token=" + token)
                        rc = rcreq.json()['RatingCurves'][0]['Id']
                    except:
                        rc = ''
                        print "error while getting rating curve number"

                    rcId = rc

                    # control condition
                    try:
                        controlCond = fieldVisitData['ControlConditionActivity']['ControlCondition']
                    except:
                        controlCond = ''

                    # activityRemark
                    try:
                        activityRemark = fieldVisitData['Remarks']
                    except:
                        activityRemark = ''
                    locationRemark = ''
                    activityRemark = activityRemark.encode('utf-8').replace('\xd0', 'deg')
                    fieldDateDischargelist.append(str(locationId) + ',')
                    fieldDateDischargelist.append(str(locationName) + ',')
                    fieldDateDischargelist.append(str(date) + ',')
                    fieldDateDischargelist.append(str(activity) + ',')
                    fieldDateDischargelist.append(str(meanTime) + ',')
                    fieldDateDischargelist.append(str(tz) + ',')
                    fieldDateDischargelist.append(str(stage) + ',')
                    fieldDateDischargelist.append(str(fieldVisitDischarge) + ',')
                    fieldDateDischargelist.append(str(rcId) + ',')
                    fieldDateDischargelist.append(str(shift) + ',')
                    fieldDateDischargelist.append(str(controlCond) + ',')
                    fieldDateDischargelist.append(str(activityRemark).replace("," , "").replace("\n", " ").replace("\r", " ").replace("==Aggregated measurement activity remarks:  ", "") + ',')
                    fieldDateDischargelist.append(str(locationRemark) + ',')
                    fieldDateDischargelist.append(' ' + '\n')
                    fieldVisitInfoList.append(fieldDateDischargelist)
                    print "Add Discharge"
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass
else:
    pass
path = "C:\\_dev"
if len(fieldVisitInfoList) > 0:
    while True:
        try:
            print "output file"
            outputfile = open(path + '\\' + "LastFV" + "_ON_10_14.csv", "wb")
            outputfile.write('Location ID, Location Name, Date, Activity, Time, UTC offset, Stage|m, Discharge|m^3/s, RC No, Shift, Control Condition, Activity Remarks, Location Remarks\n')
            for m in fieldVisitInfoList:
                for n in m:
                    outputfile.write(n)
            outputfile.close()
            break
        except IOError:
            print "Could not open file! Please close Excel!"
            break
print "DONE"