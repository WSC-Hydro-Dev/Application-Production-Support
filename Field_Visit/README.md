## Functions Overview:

### 1. `getSession()`
- **Purpose:** Establishes a session with the AQ service using login credentials.
- **Parameters:** None
- **Returns:** An active session object (`timeseries_client`) for further API interactions.

### 2. `wipeCSV()`
- **Purpose:** Clears the contents of the specified CSV file.
- **Parameters:** None
- **Returns:** None

### 3. `getFieldVisitDescriptionList(s)`
- **Purpose:** Retrieves field visit descriptions, including unique identifiers, station information, and start times, from the AQ service within a specified date range.
- **Parameters:** 
  - `s` (Session object) - Active session with the AQ service.
- **Returns:** A list of tuples containing unique identifier, station, and start time pairs.

### 4. `getFieldVisitData(s)`
- **Purpose:** Fetches field visit data for each unique identifier obtained from `getFieldVisitDescriptionList(s)` and writes it to a CSV file.
- **Parameters:** 
  - `s` (Session object) - Active session with the AQ service.
- **Returns:** None

---

The script is designed to interact with an AQ service to fetch field visit data, including unique identifiers, station information, start times, and the presence of images during the field visit. The data is then organized and written to a CSV file. 

The sequence to use these functions is as follows:
1. Establish a session with the AQ service using `getSession()`.
2. Retrieve field visit descriptions using `getFieldVisitDescriptionList(s)`.
3. Fetch field visit data and write it to a CSV file using `getFieldVisitData(s)`.

Ensure to provide the necessary AQ URL, login credentials, and specific date ranges before running these functions. The script utilizes the `timeseries_client` library for API interactions and includes error handling for potential HTTP errors during the process.