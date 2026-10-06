from pathlib import Path


class CSVStorage:
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def build_file_path(self, output_prefix, trade_date):
        """
        Build a deterministic CSV filename using dataset name and date.
        """
        date_string = trade_date.strftime("%Y-%m-%d")

        return (
            self.data_directory
            / f"{output_prefix}_{date_string}.csv"
        )

    def save_dataframe(self, dataframe, output_prefix, trade_date):
        """
        Save a DataFrame to a CSV file.

        Existing files for the same dataset and date are replaced.
        """
        file_path = self.build_file_path(
            output_prefix,
            trade_date
        )

        dataframe.to_csv(
            file_path,
            index=False
        )

        return file_path