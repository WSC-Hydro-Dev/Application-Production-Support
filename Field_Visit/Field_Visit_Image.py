import csv
from datetime import datetime as dt
from timeseries_client import timeseries_client
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
import time


AQ_base_url = "https://wsc.aquaticinformatics.net"
AQ_time = '%Y-%m-%dT%H:%M:%S'
csv_file = "data.csv"


def getSession():
    loginID = ''  # login id
    password = ''  # login password
    s = timeseries_client(AQ_base_url, loginID, password)
    return s


def wipeCSV():
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        pass


def getFieldVisitDescriptionList(s):
    Identifier_Station_Time_Pairs = []

    try:
        current_date = datetime.now()
        query_from_date = datetime(2012, 1, 1)
        while query_from_date < current_date:
            query_to_date = query_from_date + timedelta(days=3 * 365)  # Add 3 years to the from date
            if query_to_date > current_date:
                query_to_date = current_date

            parameters = {'QueryFrom': query_from_date.strftime('%Y-%m-%d'),
                          'QueryTo': query_to_date.strftime('%Y-%m-%d')}
            data = s.publish.get('/GetFieldVisitDescriptionList', params=parameters)

            if 'FieldVisitDescriptions' in data:
                for item in data['FieldVisitDescriptions']:
                    identifier = item['Identifier']
                    station = item['LocationIdentifier']
                    start_time = item['StartTime']
                    Identifier_Station_Time_Pairs.append((identifier, station, start_time))

            query_from_date = query_to_date + timedelta(days=1)
            time.sleep(1)

    except HTTPError as e:
        print("Failed at getting unique ID")
        print(e)
        pass

    return Identifier_Station_Time_Pairs


def getFieldVisitData(s):
    Identifier_Station_Time_Pairs = getFieldVisitDescriptionList(s)
    print(Identifier_Station_Time_Pairs)
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Station ID', 'Field Visit Date', 'Image', 'Year']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for identifier, station, start_time in Identifier_Station_Time_Pairs:
            parameters = {'FieldVisitIdentifier': identifier}
            data = s.publish.get('/GetFieldVisitData', params=parameters)

            if data and 'Attachments' in data:
                attachments = data['Attachments']
                image_found = any(attachment['AttachmentType'] == 'Image' for attachment in attachments)

                field_visit_date = start_time.split('T')[0]
                field_visit_year = int(field_visit_date.split('-')[0])

                writer.writerow({
                    'Station ID': station,
                    'Field Visit Date': field_visit_date,
                    'Image': 'Yes' if image_found else 'No',
                    'Year': field_visit_year
                })
            else:
                print("No attachments found for identifier:", identifier)

    print("CSV file created with required data.")


if __name__ == "__main__":
    wipeCSV()
    s = getSession()
    getFieldVisitData(s)
    s.disconnect()

    print('end at:')
    print(dt.now())
