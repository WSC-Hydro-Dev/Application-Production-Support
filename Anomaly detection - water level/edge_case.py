import os

from owslib.ogcapi.features import Features
import pandas as pd
from tabulate import tabulate


def detect_anomalies(date, values):
    non_null_values = [value for value in values if pd.notnull(value)]

    if not non_null_values:
        print("No valid values for anomaly detection.")
        return pd.DataFrame()

    mean_value = sum(non_null_values) / len(non_null_values)
    std_deviation = (sum((x - mean_value) ** 2 for x in non_null_values) / len(non_null_values)) ** 0.5
    threshold = 2 * std_deviation

    print("Mean:", mean_value)
    print("Standard Deviation:", std_deviation)
    print("Threshold:", threshold)

    edge_scenarios = []

    for i in range(1, len(values)):
        if pd.notnull(values[i]) and pd.notnull(values[i - 1]):
            diff = abs(values[i] - values[i - 1])
            if diff > threshold:
                edge_scenarios.append({
                    'timestamp': date[i],
                    'value': values[i],
                    'previous_value': values[i - 1],
                    'difference': diff
                })

    edge_scenarios.sort(key=lambda x: x['timestamp'])
    anomalies = pd.DataFrame(edge_scenarios)
    return anomalies


def fetch_hydrometric_data(station):
    oafeat = Features("https://api.weather.gc.ca/")
    hydrometric_data = {}
    offset = 0
    batch_size = 500
    all_data_fetched = False

    while not all_data_fetched:
        hydro_data = oafeat.collection_items(
            "hydrometric-daily-mean",
            STATION_NUMBER=station,
            limit=batch_size,
            offset=offset,
        )
        if hydro_data["features"]:
            historical_data_format = [
                {
                    "DATE": el["properties"]["DATE"],
                    "LEVEL": el["properties"]["LEVEL"],
                }
                for el in hydro_data["features"]
            ]

            historical_data_df = pd.DataFrame(
                historical_data_format,
                columns=[
                    "DATE",
                    "LEVEL",
                ],
            )
            historical_data_df["DATE"] = pd.to_datetime(historical_data_df["DATE"])
            historical_data_df.set_index(["DATE"], inplace=True)

            if station not in hydrometric_data:
                hydrometric_data[station] = historical_data_df
            else:
                hydrometric_data[station] = pd.concat([hydrometric_data[station], historical_data_df])

            offset += batch_size
            if offset >= hydro_data["numberMatched"]:
                all_data_fetched = True

    return hydrometric_data

def main():
    station_numbers = input("Enter station numbers separated by comma: ").split(',')
    csv_file = "anomalies_data.csv"

    for station in station_numbers:
        hydrometric_data = fetch_hydrometric_data(station)

        if station in hydrometric_data:
            displayed_df = hydrometric_data[station][["LEVEL"]].round(2).rename(
                columns={
                    "LEVEL": "Water level daily mean (m)",
                }
            )
            displayed_df.index = displayed_df.index.rename("Date")
            values = displayed_df["Water level daily mean (m)"].tolist()
            date = displayed_df.index.tolist()

            anomalies = detect_anomalies(date, values)

            anomalies_data = pd.DataFrame(anomalies)
            anomalies_data.insert(0, 'Station', station)

            if not anomalies_data.empty:
                print(f"\nAnomalies for Station {station}:")
                print(tabulate(anomalies_data, headers='keys', tablefmt='pretty'))

                # Append anomalies_data to CSV
                if not os.path.isfile(csv_file):
                    anomalies_data.to_csv(csv_file, index=False)
                else:
                    anomalies_data.to_csv(csv_file, mode='a', header=False, index=False)

                print(f"Anomalies data for Station {station} appended to {csv_file}.")
            else:
                print(f"\nNo anomalies detected for Station {station}.")
        else:
            print(f"No data found for Station {station}.")


if __name__ == "__main__":
    main()