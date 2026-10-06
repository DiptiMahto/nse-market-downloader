# NSE Market Data Downloader

A Python application that automatically retrieves and stores live NSE (National Stock Exchange of India) market-analysis data as CSV files.

The application supports the four datasets required by the internship assignment:

1. Top Gainers / Losers
2. Upper Band Hitters
3. Volume Gainers / Spurts
4. 52 Week High — Equity Market

The application uses NSE's public web APIs, validates the returned data, removes duplicate records, stores deterministic CSV files, handles request failures with retries, and continues processing other datasets when one dataset fails.

---

## Features

* Downloads all four required NSE market datasets automatically
* Supports downloading an individual dataset using the command line
* Uses NSE API endpoints discovered from the official NSE website
* Stores each dataset as a date-based CSV file
* Prevents confusing duplicate files when the application is run multiple times on the same day
* Validates API responses before saving data
* Checks for empty responses and invalid record structures
* Checks required columns such as `symbol`
* Removes duplicate records before storage
* Handles HTTP and network errors
* Retries failed requests with configurable retry count and backoff
* Logs dataset execution, record counts, successful downloads, and failures
* Isolates dataset failures so one failed dataset does not unnecessarily stop the remaining downloads
* Keeps configuration separate from application logic
* Includes automated tests using `pytest`

---

## Datasets

| Dataset                 | NSE Page                                  | API Endpoint                         |
| ----------------------- | ----------------------------------------- | ------------------------------------ |
| Top Gainers / Losers    | `/market-data/top-gainers-losers`         | `live-analysis-variations`           |
| Upper Band Hitters      | `/market-data/upper-band-hitters`         | `live-analysis-price-band-hitter`    |
| Volume Gainers / Spurts | `/market-data/volume-gainers-spurts`      | `live-analysis-volume-gainers`       |
| 52 Week High            | `/market-data/52-week-high-equity-market` | `live-analysis-data-52weekhighstock` |

The Top Gainers / Losers endpoint uses the NSE parameters:

* `index=gainers`
* `index=loosers`

`loosers` is the parameter spelling used by the NSE API.

---

## Project Structure

```text
nse-market-downloader/
│
├── config/
│   └── config.yaml
│
├── data/
│   └── *.csv
│
├── sample/
│   ├── top_gainers_losers_gainers_sample.csv
│   ├── top_gainers_losers_losers_sample.csv
│   ├── upper_band_hitters_sample.csv
│   ├── volume_gainers_spurts_sample.csv
│   └── 52_week_high_sample.csv
│
├── scripts/
│   └── run_nse_downloader.bat
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── downloader.py
│   ├── main.py
│   ├── storage.py
│   └── validator.py
│
├── tests/
│   ├── test_downloader.py
│   └── test_validator.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Architecture

The application separates the main responsibilities into different modules.

### 1. Configuration — `config/config.yaml`

Contains:

* NSE base URL
* NSE API URL
* Dataset endpoints
* Dataset parameters
* Output filenames
* Timeout
* Retry count
* Retry backoff
* Validation settings
* Logging level

This keeps URLs and configuration separate from the application logic.

### 2. Acquisition — `src/downloader.py`

Responsible for:

* Creating an NSE HTTP session
* Sending API requests
* Applying request timeouts
* Retrying failed requests
* Parsing JSON responses
* Extracting records from different NSE response structures

Each dataset has its own extraction method because the NSE APIs do not all return data in exactly the same JSON structure.

### 3. Validation — `src/validator.py`

Responsible for:

* Checking that the API response contains records
* Rejecting empty responses
* Rejecting invalid record formats
* Converting records into pandas DataFrames
* Checking required columns
* Removing duplicate records
* Ensuring data remains after validation

### 4. Storage — `src/storage.py`

Responsible for:

* Creating the output directory
* Building deterministic filenames
* Saving validated DataFrames as CSV files

### 5. Entry Point — `src/main.py`

Responsible for:

* Loading configuration
* Configuring logging
* Parsing command-line arguments
* Establishing the NSE session
* Running selected datasets
* Handling per-dataset failures
* Printing the final execution summary

---

## Requirements

* Python 3.10 or newer
* Internet connection
* Access to NSE public web APIs

Python dependencies are listed in `requirements.txt`.

---

## Installation

### 1. Open the project

Open the project directory in PyCharm or another Python IDE.

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## Running the Application

### Download all datasets

From the project root:

```powershell
python -m src.main
```

The application attempts to download all four datasets.

### Download an individual dataset

Top Gainers / Losers:

```powershell
python -m src.main --dataset top-gainers-losers
```

Upper Band Hitters:

```powershell
python -m src.main --dataset upper-band-hitters
```

Volume Gainers / Spurts:

```powershell
python -m src.main --dataset volume-gainers-spurts
```

52 Week High:

```powershell
python -m src.main --dataset 52-week-high
```

---

## Output

CSV files are stored in the `data/` directory.

Example:

```text
data/
├── top_gainers_losers_gainers_2026-10-06.csv
├── top_gainers_losers_losers_2026-10-06.csv
├── upper_band_hitters_2026-10-06.csv
├── volume_gainers_spurts_2026-10-06.csv
└── 52_week_high_2026-10-06.csv
```

The filename identifies the dataset, category where applicable, and execution date.

---

## Sample CSV Output

Representative sample outputs are included in the `sample/` directory.

```text
sample/
├── top_gainers_losers_gainers_sample.csv
├── top_gainers_losers_losers_sample.csv
├── upper_band_hitters_sample.csv
├── volume_gainers_spurts_sample.csv
└── 52_week_high_sample.csv
```

The sample files contain a small subset of the retrieved records and are provided for demonstration purposes.

Full downloaded market data is stored in the `data/` directory and is excluded from version control.

---

## Duplicate Handling

The application uses deterministic filenames based on the dataset name and date.

For example:

```text
volume_gainers_spurts_2026-10-06.csv
```

If the application is executed again on the same day, it writes to the same filename rather than creating files such as:

```text
volume_gainers_spurts_2026-10-06_1.csv
volume_gainers_spurts_2026-10-06_2.csv
```

Records returned by the API are also checked for duplicates before being stored.

This provides predictable daily snapshots while avoiding confusing duplicate files.

---

## Error Handling

The downloader handles common API and network problems including:

* Connection failures
* Request timeouts
* HTTP errors
* Invalid JSON responses
* Empty API responses
* Unexpected response structures
* Missing required columns

Failed requests are retried according to the configuration.

Default settings:

```yaml
download:
  timeout: 30
  max_retries: 3
  backoff_seconds: 2
```

---

## Retry and Backoff

Temporary request failures are handled using configurable retries.

The default behavior allows up to three attempts with a two-second delay between failed attempts.

This helps handle temporary network problems without immediately failing the dataset download.

---

## Dataset Failure Isolation

Each dataset is processed independently.

If one dataset fails, the exception is logged and the application continues with the remaining datasets.

Example:

```text
Download Summary
----------------
Successful: 3
  ✓ top-gainers-losers
  ✓ volume-gainers-spurts
  ✓ 52-week-high

Failed: 1
  ✗ upper-band-hitters
```

This prevents a failure in one API dataset from unnecessarily blocking the complete download process.

---

## Data Validation

Before a dataset is written to disk, the application validates:

1. The response exists.
2. The response is a list of records.
3. The response is not empty.
4. Each record is a dictionary.
5. Required columns are present.
6. Duplicate records are removed.
7. The resulting DataFrame is not empty.

The current required column configured for validation is:

```text
symbol
```

---

## Logging

The application uses Python's built-in `logging` module.

Example log messages:

```text
INFO - Connecting to NSE...
INFO - NSE connection successful.
INFO - Starting dataset: volume-gainers-spurts
INFO - volume-gainers-spurts: 25 records saved to data/volume_gainers_spurts_2026-10-06.csv
```

Failures are logged with the corresponding dataset and error message.

---

## Testing

The project uses `pytest` for automated testing.

Run the complete test suite:

```powershell
python -m pytest
```

The test suite covers:

### Downloader tests

* Bhavcopy filename generation
* CSV file creation
* ZIP extraction
* Retry behavior
* HTTP 404 handling
* Top Gainers / Losers extraction
* Upper Band Hitters extraction
* Volume Gainers extraction
* 52 Week High extraction
* Invalid JSON handling
* HTTP error handling

### Validator tests

* Missing response handling
* Empty response handling
* Invalid record handling
* Missing required columns
* Duplicate record removal
* DataFrame creation

Current test result:

```text
17 passed
```

---

## Configuration

Dataset and application settings are stored in:

```text
config/config.yaml
```

Example:

```yaml
download:
  data_directory: "data"
  timeout: 30
  max_retries: 3
  backoff_seconds: 2
```

This allows download behavior and API configuration to be changed without modifying the main application logic.

---

## Scheduled Execution

The application can be executed automatically on Windows using Task Scheduler.

A helper batch file is provided:

```text
scripts/run_nse_downloader.bat
```

The batch file activates the project's virtual environment and executes:

```text
python -m src.main
```

The batch file can be configured as the action in Windows Task Scheduler to run the downloader automatically at a selected time.

Scheduled execution allows periodic market-data snapshots to be collected without manually starting the application.

---

## Historical Data Management

The application uses date-based filenames to maintain daily snapshots.

For example:

```text
volume_gainers_spurts_2026-10-06.csv
volume_gainers_spurts_2026-10-07.csv
volume_gainers_spurts_2026-10-08.csv
```

This allows snapshots from different execution dates to coexist without overwriting previous days.

---

## Limitations and Assumptions

* The application retrieves the current live snapshot provided by the NSE market-analysis APIs.
* The date in the output filename represents the execution date, not a historical date requested from the API.
* Market data can change between executions during the trading session.
* NSE may change API endpoints, response structures, or access requirements in the future.
* The application depends on
