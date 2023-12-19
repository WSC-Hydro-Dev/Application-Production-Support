
ANOMALY DETECTION README

PURPOSE: The provided Python script, is designed to identify anomalies within a sequence of numerical data points with corresponding timestamps. It employs statistical measures to identify abrupt changes or outliers in the data series.

FUNCTIONALITY:

1. INPUT:
   - date: A list or array containing timestamps corresponding to each data point.
   - values: A list or array containing numerical values(Water levels) corresponding to the timestamps.


2. PREPROCESSING:
    
    Filters out null or missing values from the input data.


3. STATISTICAL ANALYSIS:
    
    Calculates the mean and standard deviation of the non-null data points.
    Determines a threshold for anomalies based on the standard deviation.


4. ANOMALY DETECTION:

    Compares each data point with its immediate preceding value to detect sudden changes.
    If the absolute difference between consecutive values exceeds the threshold, it's considered an anomaly.


OUTPUT:

    Generates a DataFrame containing information about identified anomalies:
    Timestamp of the anomaly.
    Value causing the anomaly.
    Previous value before the anomaly.
    Difference between the current and previous values.