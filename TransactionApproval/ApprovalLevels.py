import csv
from datetime import datetime as dt
from timeseries_client import timeseries_client
from requests.exceptions import HTTPError
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator


AQ_base_url = "" #AQ url
AQ_time = '%Y-%m-%dT%H:%M:%S'
csv_file = "data.csv"

def getSession():
    loginID = "" # login for AQ
    password = "" # password for AQ
    s = timeseries_client(AQ_base_url, loginID, password)
    return s

def wipeCSV():
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        pass

def getTSUniqueID(s):
    uniqueID = []
    try:
        data = s.publish.get('/GetTimeSeriesDescriptionList')
        if 'TimeSeriesDescriptions' in data:
            for i in data['TimeSeriesDescriptions']:
                if i['Parameter'] in ["Stage", "Discharge"] and i['Label'] == "Working":
                    ID = i['UniqueId']
                    uniqueID.append(ID)

    except HTTPError as e:
        print("Failed at getting unique ID")
        print(e)
        pass

    return uniqueID


def getApprovalsTransactionListData(s, unique_id):
    unique_ids = getTSUniqueID(s)
    if unique_id in unique_ids:
        fieldnames = ['ID', 'ApprovalLevel', 'DateAppliedUtc', 'User', 'LevelDescription', 'Comment', 'StartTime', 'EndTime']
        parameters = {'TimeSeriesUniqueId': unique_id}
        data = s.publish.get('/GetApprovalsTransactionList', params=parameters)

        if data:
            approvals_transactions = data.get('ApprovalsTransactions', [])

            with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        
                if csvfile.tell() == 0:
                    writer.writeheader()
                        
                for transaction in approvals_transactions:
                    writer.writerow({
                        'ID': unique_id,  
                        'ApprovalLevel': transaction.get('ApprovalLevel', ''),
                        'DateAppliedUtc': transaction.get('DateAppliedUtc', ''),
                        'User': transaction.get('User', ''),
                        'LevelDescription': transaction.get('LevelDescription', ''),
                        'Comment': transaction.get('Comment', ''),
                        'StartTime': transaction.get('StartTime', ''),
                        'EndTime': transaction.get('EndTime', ''),
                    })
    else:
        print(f"Invalid unique ID: {unique_id}.")


def queryCSV(unique_id, query_date):
    df = pd.read_csv(csv_file)
    
    df['StartTime'] = pd.to_datetime(df['StartTime'], errors='coerce', utc=True)
    df['EndTime'] = pd.to_datetime(df['EndTime'], errors='coerce', utc=True)
    df['DateAppliedUtc'] = pd.to_datetime(df['DateAppliedUtc'], errors='coerce', utc=True)
    
    filtered_df = df[(df['DateAppliedUtc'] <= query_date) & (df['ID'] == unique_id)]
    filtered_df = filtered_df.dropna(subset=['StartTime'])
    
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by='DateAppliedUtc', ascending=False)
        
        cmap = plt.cm.get_cmap('tab10')
        num_colors = len(filtered_df['DateAppliedUtc'].unique())
        
        fig, (ax, container) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            color = cmap(idx / num_colors) 
            ax.plot([row['StartTime'], row['EndTime']], [row['ApprovalLevel'], row['ApprovalLevel']], marker='o', markersize=6, color=color, linestyle='-', linewidth=0.8, label=f"Date Applied: {row['DateAppliedUtc']}")

        ax.set_ylabel('Approval Level')
        ax.set_title(f'Approval Levels till {query_date} for Unique ID {unique_id}')
        
        ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0., fontsize='small')

        x_values = pd.concat([filtered_df['StartTime'], filtered_df['EndTime']])
        x_values = sorted(x_values)
        
        ax.xaxis.set_major_locator(MaxNLocator(nbins=len(x_values)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.tick_params(axis='x', which='major', pad=6) 
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        cell_text = filtered_df[['ApprovalLevel', 'DateAppliedUtc','StartTime', 'EndTime']].astype(str).values
        columns = ['Approval Level', 'Date Applied', 'Start Time', 'End Time']
        table = container.table(cellText=cell_text, colLabels=columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.auto_set_column_width(col=list(range(len(columns))))
        table.scale(1, 1.5)  
       

        container.axis('off')

        plt.tight_layout(pad=2.0)
        plt.show()
    else:
        print(f"No data found for the specified date and unique ID.")


def updateData(unique_id):
    s = getSession()
    getApprovalsTransactionListData(s, unique_id)
    s.disconnect()

    print('end at:')
    print(dt.now())


if __name__ == "__main__":
    wipeCSV()  
    unique_id = "" # example -'d806493c8349412ba670f678a4fe2597'
    query_date = "" # example -'2023-11-2'
    updateData(unique_id)
    queryCSV(unique_id, query_date)
