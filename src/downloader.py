import io
import time
import zipfile

from pathlib import Path

import requests


class NSEDownloader:
    def __init__(self, base_url, api_url, timeout=30, max_retries=3):
        self.base_url = base_url
        self.api_url = api_url
        self.timeout = timeout
        self.max_retries = max_retries

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/154.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.base_url + "/",
        })

    def get_session(self):
        """
        Establish a session with NSE before making API requests.
        """
        response = self.session.get(
            self.base_url,
            timeout=self.timeout
        )

        response.raise_for_status()

        return response

    def get(self, endpoint, params=None):
        """
        Send a GET request to an NSE API endpoint with retries.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )

                response.raise_for_status()

                return response

            except requests.RequestException as error:
                last_error = error

                if attempt < self.max_retries:
                    time.sleep(2)

        raise last_error

    def get_url(self, url):
        """
        Send a GET request to an absolute URL with retries.
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout
                )

                response.raise_for_status()

                return response

            except requests.RequestException as error:
                last_error = error

                if attempt < self.max_retries:
                    time.sleep(2)

        raise last_error

    def download_csv(self, endpoint, file_path, params=None):
        """
        Download CSV data from an NSE endpoint and save it locally.
        """
        response = self.get(endpoint, params=params)

        return self.save_csv(
            response.content,
            file_path
        )

    def download_and_extract_zip(self, endpoint, extract_directory, params=None):
        """
        Download a ZIP archive from NSE and extract its CSV file.
        """
        response = self.get(endpoint, params=params)

        extract_path = Path(extract_directory)
        extract_path.mkdir(
            parents=True,
            exist_ok=True
        )

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            archive.extractall(extract_path)
            extracted_files = archive.namelist()

        return extracted_files

    @staticmethod
    def build_bhavcopy_filename(trade_date):
        """
        Build the current NSE UDiFF Bhavcopy filename.
        """
        date_string = trade_date.strftime("%Y%m%d")

        return (
            f"BhavCopy_NSE_CM_0_0_0_"
            f"{date_string}_F_0000.csv.zip"
        )

    def download_bhavcopy(self, trade_date, output_directory):
        """
        Download the NSE UDiFF Bhavcopy ZIP for a given trading date
        and extract the CSV into the output directory.
        """
        filename = self.build_bhavcopy_filename(trade_date)

        url = (
            "https://nsearchives.nseindia.com/"
            f"content/cm/{filename}"
        )

        output_path = Path(output_directory)
        output_path.mkdir(
            parents=True,
            exist_ok=True
        )

        zip_path = output_path / filename

        try:
            response = self.get_url(url)
        except requests.HTTPError as error:
            if error.response is not None and error.response.status_code == 404:
                raise FileNotFoundError(
                    f"No Bhavcopy found for {trade_date.strftime('%Y-%m-%d')}"
                ) from error

            raise

        zip_path.write_bytes(response.content)

        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(output_path)
            extracted_files = archive.namelist()

        zip_path.unlink()

        return extracted_files

    @staticmethod
    def save_csv(content, file_path):
        """
        Save CSV content to a file.
        """
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_bytes(content)

        return path

