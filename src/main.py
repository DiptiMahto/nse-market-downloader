"""
from config_loader import load_config
from downloader import NSEDownloader


def main():
    config = load_config()

    nse_config = config["nse"]
    download_config = config["download"]

    downloader = NSEDownloader(
        base_url=nse_config["base_url"],
        api_url=nse_config["api_url"],
        timeout=download_config["timeout"],
        max_retries=download_config["max_retries"],
    )

    print("NSE Market Data Downloader")
    print("--------------------------")
    print(f"NSE Base URL: {nse_config['base_url']}")
    print(f"NSE API URL: {nse_config['api_url']}")
    print(f"Data directory: {download_config['data_directory']}")
    print("Configuration loaded successfully.")


if __name__ == "__main__":
    main()
"""
import argparse
import logging
from datetime import datetime

from config_loader import load_config
from downloader import NSEDownloader

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Download NSE market Bhavcopy data."
    )

    parser.add_argument(
        "trade_date",
        help="Trading date in YYYY-MM-DD format"
    )

    return parser.parse_args()

def main():
    config = load_config()

    logging_config = config["logging"]

    logging.basicConfig(
        level=getattr(
            logging,
            logging_config["level"].upper(),
            logging.INFO
        ),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    nse_config = config["nse"]
    download_config = config["download"]

    print("NSE Market Data Downloader")
    print("--------------------------")

    args = parse_arguments()

    try:
        trade_date = datetime.strptime(
            args.trade_date,
            "%Y-%m-%d"
        )
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    if trade_date.weekday() >= 5:
        print("The selected date is a weekend.")
        print("Please provide a trading day (Monday-Friday).")
        return

    downloader = NSEDownloader(
        base_url=nse_config["base_url"],
        api_url=nse_config["api_url"],
        timeout=download_config["timeout"],
        max_retries=download_config["max_retries"],
    )

    try:
        logger.info("Connecting to NSE...")
        downloader.get_session()
        logger.info("NSE connection successful.")

        logger.info(
            f"Downloading Bhavcopy for "
            f"{trade_date.strftime('%Y-%m-%d')}..."
        )

        extracted_files = downloader.download_bhavcopy(
            trade_date=trade_date,
            output_directory=download_config["data_directory"]
        )

    except Exception as error:
        print(f"Error: Unable to download Bhavcopy.")
        print(f"Reason: {error}")
        return

    logger.info("Download successful!")
    logger.info("Extracted files:")

    for file in extracted_files:
        logger.info(f"- {file}")

if __name__ == "__main__":
    main()