# NSE Market Data Downloader

A Python application that downloads and extracts NSE (National Stock Exchange of India) equity market Bhavcopy data for a specified trading date.

## Features

- Download NSE Bhavcopy data for a given date
- Uses the current NSE UDiFF Bhavcopy format
- Extracts the CSV file from the downloaded ZIP archive
- Configurable download directory, timeout, retry count, and logging level
- Command-line interface for date input
- Validates date format
- Prevents weekend dates from being submitted
- Retries failed HTTP requests
- Handles unavailable Bhavcopy data with a clear error message
- Automated unit tests using pytest

## Project Structure

```text
nse-market-downloader/
│
├── config/
│   └── config.yaml
│
├── data/
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── downloader.py
│   └── main.py
│
├── tests/
│   └── test_downloader.py
│
├── .gitignore
├── README.md
└── requirements.txt