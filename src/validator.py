import pandas as pd


class DataValidator:
    def __init__(self, required_columns=None):
        self.required_columns = required_columns or []

    def validate_records(self, records):
        """
        Validate that the API returned a non-empty list of records.
        """
        if records is None:
            raise ValueError("Response data is missing.")

        if not isinstance(records, list):
            raise ValueError("Response data must be a list of records.")

        if not records:
            raise ValueError("Response data is empty.")

        if not all(isinstance(record, dict) for record in records):
            raise ValueError("Response contains invalid record format.")

        return True

    def to_dataframe(self, records):
        """
        Convert validated records into a pandas DataFrame.
        """
        self.validate_records(records)

        dataframe = pd.DataFrame(records)

        if dataframe.empty:
            raise ValueError("DataFrame is empty.")

        missing_columns = [
            column
            for column in self.required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        dataframe = dataframe.drop_duplicates()

        if dataframe.empty:
            raise ValueError("No data remains after duplicate handling.")

        return dataframe