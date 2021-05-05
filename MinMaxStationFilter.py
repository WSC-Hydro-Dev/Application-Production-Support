import grequests
# grequests to speed up request API
import csv
import timeit

match_dic = {
    "Program Type": "HYDROMETRIC",
    "Station Use": "REAL TIME",
    "End Year": ""
}
# dictionary for filtering

def filtering(file_name):
    filtered = []
    match_list = []
    category_list = []
    found = True

    with open(file_name) as f:
        data = csv.reader(f)
        category = next(data)
        for x in match_dic:
            if x in category:
                match_list.append(category.index(x))
                category_list.append(x)

        for x in data:
            for y in range(len(match_list)):
                if x[match_list[y]] != match_dic[category_list[y]]:
                    found = False
            if found:
                filtered.append(x[0])
            else:
                found = True
    return filtered
# filter the station

def open_filter(lst):
    a = filtering(lst[0])
    b = filtering(lst[1])

    filtered = set(a) & set(b)

    return list(filtered)
# filter individual stations in the files

def unique_id(id_lst):
    url = "https://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2"
    func = "/GetTimeSeriesDescriptionList"
    para = "?Parameter=Stage&LocationIdentifier="
    username = "username" # need to be replaced by working username
    password = "password" # need to be replaced by working password
    url_lst = []
    unique_lst = []

    for i in id_lst:
        url_lst.append(url + func + para + str(i))
    rs = (grequests.get(u, auth=(username, password)) for u in url_lst)
    responses = grequests.map(rs)

    for response in responses:
        data = response.json()
        found = False
        if "TimeSeriesDescriptions" in data:
            description = response.json()["TimeSeriesDescriptions"]
            for x in description:
                if "Stage.Working@" in x["Identifier"]:
                    unique_lst.append(x["UniqueId"])
                    found = True
                    break
        if not found:
            unique_lst.append("None")
    return unique_lst
# Access API to get Unique Id of the station filtered

def min_max(id_lst, year_lst):
    url = "https://wsc.aquaticinformatics.net/AQUARIUS/Publish/v2"
    func = "/GetTimeSeriesData"
    para = "?TimeSeriesUniqueIds="
    username = "username"  # need to be replaced by working username
    password = "password"  # need to be replaced by working password
    url_lst = []
    val_lst = []
    min_max_lst = []
    total_lst = []

    for year in year_lst:
        time_from = "&QueryFrom=" + str(year) + "-01-01"
        time_to = "&QueryTo=" + str(year) + "-12-31"
        for i in id_lst:
            url_lst.append(url + func + para + str(i) + time_from + time_to)
        rs = (grequests.get(u, auth=(username, password)) for u in url_lst)
        responses = grequests.map(rs)

        for response in responses:
            data = response.json()
            if "Points" in data:
                for x in data["Points"]:
                    val_lst.append(x["NumericValue1"])

            if val_lst:
                min_val = str(round(min(val_lst), 3))
                max_val = str(round(max(val_lst), 3))
            else:
                min_val = "None"
                max_val = "None"
            min_max_lst.append(min_val + "," + max_val)
            val_lst = []
        total_lst.append(min_max_lst)
        min_max_lst = []
        url_lst = []
    return total_lst
# Access API to get Minimum and Maximum of each year in the list

def make_csv(station_lst, value_list):
    csv_file = open("Final_Result.csv", "a")

    for x in range(len(station_lst)):
        data = station_lst[x]
        for year in value_list:
            data += "," + year[x]
        csv_file.write(data + "\n")
    csv_file.close()
# create the csv file with the stations and min/max values

def main():
    file_lst = ["hydex_use_report_2021-01-28.csv", "hydex_program_record_report_2021-01-28.csv"]
    result = open_filter(file_lst)
    result.sort()
    print "All station filtered " + str(len(result))
    years = [2013, 2014, 2015, 2016, 2017, 2018]

    csvf = open("Final_Result.csv", "w")
    title = "StationID"
    for year in years:
        title += "," + str(year) + " Min" + "," + str(year) + " Max"
    title += "\n"
    csvf.write(title)
    csvf.close()
    for x in range(len(result) / 10 + 1):
        print str(x) + "th set preparing"
        a = x * 10
        b = min(x*10 + 10, len(result))
        make_csv(result[a:b], min_max(unique_id(result[a:b]), years))
    print "Done"


if __name__ == '__main__':
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print("Time: ", stop - start)
