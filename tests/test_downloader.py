from datetime import datetime

import pytest
import requests
import responses

from src.downloader import NSEDownloader


def test_build_bhavcopy_filename():
    trade_date = datetime(2026, 9, 25)

    filename = NSEDownloader.build_bhavcopy_filename(
        trade_date
    )

    assert filename == (
        "BhavCopy_NSE_CM_0_0_0_20260925_F_0000.csv.zip"
    )


def test_save_csv(tmp_path):
    content = b"SYMBOL,PRICE\nTEST,100\n"

    file_path = tmp_path / "test.csv"

    saved_path = NSEDownloader.save_csv(
        content,
        file_path
    )

    assert saved_path.exists()
    assert saved_path.read_bytes() == content

def test_download_and_extract_zip(tmp_path):
    import io
    import zipfile

    csv_content = b"SYMBOL,PRICE\nTEST,100\n"

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr(
            "test.csv",
            csv_content
        )

    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api"
    )

    # Mock the get() method so no real NSE request is made.
    class FakeResponse:
        content = zip_buffer.getvalue()

    downloader.get = lambda endpoint, params=None: FakeResponse()

    extract_directory = tmp_path / "extracted"

    extracted_files = downloader.download_and_extract_zip(
        endpoint="test",
        extract_directory=extract_directory
    )

    assert "test.csv" in extracted_files

    extracted_file = extract_directory / "test.csv"

    assert extracted_file.exists()
    assert extracted_file.read_bytes() == csv_content

def test_get_url_retries_on_failure(monkeypatch):
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=3
    )

    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self):
            return None

    def fake_get(*args, **kwargs):
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise requests.RequestException("Temporary error")

        return FakeResponse()

    monkeypatch.setattr(
        downloader.session,
        "get",
        fake_get
    )

    response = downloader.get_url(
        "https://example.com/test"
    )

    assert response is not None
    assert attempts["count"] == 3

def test_download_bhavcopy_raises_file_not_found_on_404(monkeypatch, tmp_path):
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api"
    )

    response = requests.Response()
    response.status_code = 404
    response.url = "https://example.com/not-found"

    def fake_get_url(url):
        error = requests.HTTPError(
            "404 Client Error: Not Found",
            response=response
        )
        raise error

    monkeypatch.setattr(
        downloader,
        "get_url",
        fake_get_url
    )

    trade_date = datetime(2026, 1, 2)

    try:
        downloader.download_bhavcopy(
            trade_date,
            tmp_path
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError as error:
        assert str(error) == "No Bhavcopy found for 2026-01-02"

def test_download_top_gainers_losers():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    gainers_response = {
        "legends": [],
        "NIFTY": {
            "data": [
                {
                    "symbol": "ABC",
                    "ltp": 100,
                    "perChange": 5.2
                }
            ]
        }
    }

    losers_response = {
        "legends": [],
        "NIFTY": {
            "data": [
                {
                    "symbol": "XYZ",
                    "ltp": 80,
                    "perChange": -4.5
                }
            ]
        }
    }

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-variations?index=gainers",
            json=gainers_response,
            status=200
        )

        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-variations?index=loosers",
            json=losers_response,
            status=200
        )

        result = downloader.download_top_gainers_losers(
            "live-analysis-variations"
        )

    assert len(result["gainers"]) == 1
    assert result["gainers"][0]["symbol"] == "ABC"

    assert len(result["losers"]) == 1
    assert result["losers"][0]["symbol"] == "XYZ"


def test_download_upper_band_hitters():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    response_data = {
        "upper": {
            "AllSec": {
                "data": [
                    {
                        "symbol": "ABC",
                        "ltp": 100,
                        "pChange": 5.0
                    }
                ]
            }
        }
    }

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-price-band-hitter",
            json=response_data,
            status=200
        )

        result = downloader.download_upper_band_hitters(
            "live-analysis-price-band-hitter"
        )

    assert len(result) == 1
    assert result[0]["symbol"] == "ABC"


def test_download_volume_gainers():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    response_data = {
        "data": [
            {
                "symbol": "ABC",
                "volume": 100000,
                "ltp": 100
            }
        ]
    }

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-volume-gainers",
            json=response_data,
            status=200
        )

        result = downloader.download_volume_gainers(
            "live-analysis-volume-gainers"
        )

    assert len(result) == 1
    assert result[0]["symbol"] == "ABC"


def test_download_52_week_high():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    response_data = {
        "data": [
            {
                "symbol": "ABC",
                "ltp": 100
            }
        ]
    }

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-data-52weekhighstock",
            json=response_data,
            status=200
        )

        result = downloader.download_52_week_high(
            "live-analysis-data-52weekhighstock"
        )

    assert len(result) == 1
    assert result[0]["symbol"] == "ABC"


def test_invalid_json_response():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-volume-gainers",
            body="This is not valid JSON",
            status=200
        )

        with pytest.raises(ValueError, match="invalid JSON"):
            downloader.get_json(
                "live-analysis-volume-gainers"
            )


def test_http_error():
    downloader = NSEDownloader(
        base_url="https://www.nseindia.com",
        api_url="https://www.nseindia.com/api",
        max_retries=1,
        backoff_seconds=0
    )

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://www.nseindia.com/api/"
            "live-analysis-volume-gainers",
            status=500
        )

        with pytest.raises(requests.HTTPError):
            downloader.get(
                "live-analysis-volume-gainers"
            )