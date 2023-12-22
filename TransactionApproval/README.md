
## Functions Overview:

### 1. `getSession()`
- **Purpose:** Establishes a session with the AQ service using login credentials.
- **Parameters:** None
- **Returns:** An active session object (`timeseries_client`) for further API interactions.

### 2. `wipeCSV()`
- **Purpose:** Clears the contents of the specified CSV file.
- **Parameters:** None
- **Returns:** None

### 3. `getTSUniqueID(s)`
- **Purpose:** Retrieves unique IDs for specified parameters and labels from the AQ service.
- **Parameters:** `s` (Session object)
- **Returns:** A list of unique IDs corresponding to specified parameters and labels.

### 4. `getApprovalsTransactionListData(s, unique_id)`
- **Purpose:** Fetches approval transaction data for a given unique ID from the AQ service and writes it to a CSV file.
- **Parameters:** 
  - `s` (Session object)
  - `unique_id` (String) - Unique identifier for a specific time series data.
- **Returns:** None

### 5. `queryCSV(unique_id, query_date)`
- **Purpose:** Queries the CSV file to extract approval level data for a specific unique ID and date.
- **Parameters:** 
  - `unique_id` (String) - Unique identifier for a specific time series data.
  - `query_date` (String) - Date for which the approval level data is requested.
- **Returns:** Displays a plot and table representing approval levels till the specified date for the given unique ID.

### 6. `updateData(unique_id)`
- **Purpose:** Initiates the data update process by fetching and updating approval transaction data for the specified unique ID.
- **Parameters:** 
  - `unique_id` (String) - Unique identifier for a specific time series data.
- **Returns:** None

---

The script is designed to interact with an AQ service to fetch approval transaction data for specific unique IDs, update a CSV file with this data, and allow querying this data for visual representation and analysis using Matplotlib.

The sequence to use these functions is as follows:
1. Establish a session with the AQ service using `getSession()`.
2. Update approval transaction data for a specific unique ID using `updateData(unique_id)`.
3. Query the CSV file for approval levels till a specified date for the given unique ID using `queryCSV(unique_id, query_date)`.

Ensure to provide the necessary AQ URL, login credentials, and specific unique IDs and dates before running these functions.