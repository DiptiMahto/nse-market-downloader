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
* Applying request timeout
