import argparse
import logging
from datetime import datetime
from pathlib import Path

from src.config_loader import load_config
from src.downloader import NSEDownloader
from src.storage import CSVStorage
from src.validator import DataValidator


def parse_arguments(dataset_names):
    parser = argparse.ArgumentParser(
        description="Download NSE market data datasets."
    )

    parser.add_argument(
        "--dataset",
        choices=["all"] + dataset_names,
        default="all",
        help="Dataset to download. Default: all"
    )

    return parser.parse_args()


def configure_logging(logging_config):
    logging.basicConfig(
        level=getattr(
            logging,
            logging_config["level"].upper(),
            logging.INFO
        ),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def download_dataset(
    dataset_name,
    dataset_config,
    downloader,
    validator,
    storage,
    trade_date,
    logger
):
    endpoint = dataset_config["endpoint"]
    output_prefix = dataset_config["output_prefix"]

    logger.info(
        f"Starting dataset: {dataset_name}"
    )

    if dataset_name == "top-gainers-losers":
        result = downloader.download_top_gainers_losers(
            endpoint
        )

        saved_files = []

        for category, records in result.items():
            dataframe = validator.to_dataframe(records)

            category_prefix = (
                f"{output_prefix}_{category}"
            )

            file_path = storage.save_dataframe(
                dataframe,
                category_prefix,
                trade_date
            )

            logger.info(
                f"{dataset_name} - {category}: "
                f"{len(dataframe)} records saved to {file_path}"
            )

            saved_files.append(file_path)

        return saved_files

    if dataset_name == "upper-band-hitters":
        records = downloader.download_upper_band_hitters(
            endpoint
        )

    elif dataset_name == "volume-gainers-spurts":
        records = downloader.download_volume_gainers(
            endpoint
        )

    elif dataset_name == "52-week-high":
        records = downloader.download_52_week_high(
            endpoint
        )

    else:
        raise ValueError(
            f"Unsupported dataset: {dataset_name}"
        )

    dataframe = validator.to_dataframe(records)

    file_path = storage.save_dataframe(
        dataframe,
        output_prefix,
        trade_date
    )

    logger.info(
        f"{dataset_name}: "
        f"{len(dataframe)} records saved to {file_path}"
    )

    return [file_path]


def main():
    config = load_config()

    configure_logging(
        config["logging"]
    )

    logger = logging.getLogger(__name__)

    nse_config = config["nse"]
    download_config = config["download"]
    datasets_config = config["datasets"]
    validation_config = config["validation"]

    args = parse_arguments(
        list(datasets_config.keys())
    )

    trade_date = datetime.now()

    data_directory = Path(
        download_config["data_directory"]
    )

    downloader = NSEDownloader(
        base_url=nse_config["base_url"],
        api_url=nse_config["api_url"],
        timeout=download_config["timeout"],
        max_retries=download_config["max_retries"],
        backoff_seconds=download_config["backoff_seconds"]
    )

    validator = DataValidator(
        required_columns=validation_config[
            "required_columns"
        ]
    )

    storage = CSVStorage(
        data_directory
    )

    print("NSE Market Data Downloader")
    print("--------------------------")
    print(
        f"Execution date: "
        f"{trade_date.strftime('%Y-%m-%d')}"
    )
    print(
        f"Data directory: "
        f"{data_directory}"
    )
    print(
        f"Dataset: {args.dataset}"
    )
    print()

    try:
        logger.info("Connecting to NSE...")
        downloader.get_session()
        logger.info("NSE connection successful.")

    except Exception as error:
        logger.error(
            f"Unable to establish NSE session: {error}"
        )
        return

    if args.dataset == "all":
        datasets_to_download = list(
            datasets_config.keys()
        )
    else:
        datasets_to_download = [
            args.dataset
        ]

    successful_datasets = []
    failed_datasets = []

    for dataset_name in datasets_to_download:

        try:
            download_dataset(
                dataset_name=dataset_name,
                dataset_config=datasets_config[
                    dataset_name
                ],
                downloader=downloader,
                validator=validator,
                storage=storage,
                trade_date=trade_date,
                logger=logger
            )

            successful_datasets.append(
                dataset_name
            )

        except Exception as error:
            failed_datasets.append(
                dataset_name
            )

            logger.error(
                f"{dataset_name} failed: {error}"
            )

    print()
    print("Download Summary")
    print("----------------")

    print(
        f"Successful: "
        f"{len(successful_datasets)}"
    )

    for dataset in successful_datasets:
        print(f"  ✓ {dataset}")

    print(
        f"Failed: "
        f"{len(failed_datasets)}"
    )

    for dataset in failed_datasets:
        print(f"  ✗ {dataset}")


if __name__ == "__main__":
    main()