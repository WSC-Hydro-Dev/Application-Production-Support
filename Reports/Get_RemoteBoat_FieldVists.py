from timeseries_client import timeseries_client
from datetime import datetime as dt
from lxml import etree
import requests

# This script queries all field visits with Remote Controlled Boat as the deployment method
# and Track Reference as VTG or GGA after a specifiable date
# It prints the Field visit date, station ID, latitude and longitude, office location, and province 
# of all of these field visits in a text file
# It also counts the number of ADCP field visits, Remote Controlled Boat field visits, and VTG/GGA Remote Controlled Boat field visits
# It also double checks whether the eHSN xml stored with the field visit has deployment method listed as
# Remote Controlled boat when the Aquarius API does via /GetFieldVisitData and will print the field visit ID if they do not natch
# The Script requires the timeseries_client module

AQ_base_url = "https://wsc.aquaticinformatics.net"

# Credentials
loginID = "username" # replace with a valid username
password = "password" # replace with a valid password


# Get the Aquarius session object
# This object will be used to send get requests to Aquarius
def getSession():

    # Get credentials
    # This uses the python wrapper for Aquarius
    s = timeseries_client(AQ_base_url, loginID, password)

    # Return the session
    return s


def getData():
    # Get the Aquarius session
    s = getSession()
    file = open("RemoteBoatQueries.txt", "x") # Create an error if the text file already exists to prevent overwriting
    print("Script Started " + dt.now().strftime("%H:%M:%S"))

    TotalADCPs = 0
    RCBoatADCPs = 0
    xmlRCBoatADCPs = 0
    VTG_GGA_RCBoat = 0

    past_date = dt(2022, 1, 1) # replace with any other date to get field visits from that date to present instead
    # today_date = dt.now()
    start_date = past_date.strftime("%Y-%m-%d")
    # end_date = today_date.strftime('%Y-%m-%d')

    parameters = {"QueryFrom": start_date}
    data = s.publish.get(
        "/GetFieldVisitDescriptionList", params=parameters
    )  # get field data on and after the start date

    for field in data["FieldVisitDescriptions"]:  # loop through each field visit
        RCBoatADCP = False

        # using each field data identifier, get more details on each field visit
        parameters = {"FieldVisitIdentifier": field["Identifier"]}
        fieldData = s.publish.get("/GetFieldVisitData", params=parameters)

        if (
            len(fieldData["DischargeActivities"]) > 0
            and len(fieldData["DischargeActivities"][0]["AdcpDischargeActivities"]) > 0
            and fieldData["DischargeActivities"][0]["AdcpDischargeActivities"][0]["AdcpDeviceType"] == "ADCP"
        ):  # check if device type is ADCP
            TotalADCPs += 1  # add 1 to total adcp counter

            deployMethod = fieldData["DischargeActivities"][0]["AdcpDischargeActivities"][0]["DischargeChannelMeasurement"]["DeploymentMethod"]

            if deployMethod == "RemoteControlledBoat":
                RCBoatADCPs += 1  # add 1 to remote boat counter
                RCBoatADCP = True

            # loop through all attachments to find eHSN xml
            for attachment in fieldData["Attachments"]:
                if attachment["AttachmentType"] == "FieldDataPlugin":
                    url = (
                        "https://wsc.aquaticinformatics.net/AQUARIUS/"
                        + attachment["Url"][6:]
                    )

                    # Get the xml content
                    eHSNxml = requests.get(url, auth=(loginID, password))

                    parser = etree.XMLParser(recover=True) # recover option: if xml is invalid, continue, deals with problematic characters like \x08
                    root = etree.fromstring(eHSNxml.content, parser=parser) # parse the xml

                    if root is not None: # avoids invalid/nonexistant xmls
                        if (
                            root.find("InstrumentDeployment").find("GeneralInfo") != None
                            and root.find("./InstrumentDeployment/GeneralInfo/deployment").text == "Remote Control"
                        ):
                            xmlRCBoatADCPs += 1

                            if not RCBoatADCP:
                                print(
                                    "xmlRCBoatADCP, but not RCBoatADCP, field visit: "
                                    + field["Identifier"]
                                )

                        elif RCBoatADCP:
                            print(
                                "RCBoatADCP, but not xmlRCBoatADCP, field visit: "
                                + field["Identifier"]
                            )

                        if (
                            RCBoatADCP
                            and root.find("./MovingBoatMeas").find("trackRefChoice") != None
                            and (
                                root.find("./MovingBoatMeas/trackRefChoice").text == "GGA"
                                or root.find("./MovingBoatMeas/trackRefChoice").text == "VTG"
                            )
                        ):
                            VTG_GGA_RCBoat += 1

                            # print field visit date
                            file.write(
                                fieldData["DischargeActivities"][0]["AdcpDischargeActivities"]
                                [0]["DischargeChannelMeasurement"]["StartTime"][:10]
                                + " "
                            )

                            # print station number
                            file.write(field["LocationIdentifier"] + " ")

                            # get station location data
                            parameters = {"LocationIdentifier": field["LocationIdentifier"]}
                            locData = s.publish.get("/GetLocationData", params=parameters)

                            # print latitude and logitude
                            if locData["Latitude"] != None and locData["Longitude"] != None:
                                file.write(
                                    str(locData["Latitude"])
                                    + " "
                                    + str(locData["Longitude"])
                                    + " "
                                )
                            else:
                                file.write("N/A ")

                            # print office
                            if (
                                len(locData["ExtendedAttributes"]) >= 1
                                and locData["ExtendedAttributes"][0].get("Value") != None
                            ):
                                file.write(locData["ExtendedAttributes"][0]["Value"] + " ")
                            else:
                                file.write("N/A ")

                            # print province
                            if (
                                len(locData["ExtendedAttributes"]) >= 2
                                and locData["ExtendedAttributes"][1].get("Value") != None
                            ):
                                file.write(locData["ExtendedAttributes"][1]["Value"] + "\n")
                            else:  # if province isn't in location details (occurs in some rare cases) then use location description list folder
                                parameters = {
                                    "LocationIdentifier": field["LocationIdentifier"]
                                }
                                locData = s.publish.get(
                                    "/GetLocationDescriptionList", params=parameters
                                )  # get station location data
                                if (
                                    len(locData["LocationDescriptions"]) >= 1
                                    and locData["LocationDescriptions"][0].get("PrimaryFolder") != None
                                ):
                                    file.write(
                                        locData["LocationDescriptions"][0]["PrimaryFolder"].split(".")[1]
                                        + "\n"
                                    )  # print province
                                else:
                                    file.write("N/A\n")

                    else:
                        print(
                            "Invalid XML/XML not found, field visit: "
                            + field["Identifier"]
                        )

    print("Number of RCBoat ADCP Field Visits: ", RCBoatADCPs)
    print("Number of RCBoat ADCP Field Visits according to xml: ", xmlRCBoatADCPs)
    print(
        "Number of RCBoat ADCP Field Visits with VTG/GGA Track Reference: ",
        VTG_GGA_RCBoat,
    )
    print("Total ADCP Field Visits: ", TotalADCPs)
    print("-------------")
    if TotalADCPs != 0:
        print(
            "Approximate Percentage of RCBoat ADCP Field Vists: %.3f%%"
            % float(RCBoatADCPs / TotalADCPs)
        )

    file.close()
    print("Script Successfully Completed! " + dt.now().strftime("%H:%M:%S"))


getData()
