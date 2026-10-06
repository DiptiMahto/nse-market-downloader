import pandas as pd
import pytest

from src.validator import DataValidator


def test_validate_records_rejects_none():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    with pytest.raises(ValueError, match="Response data is missing"):
        validator.validate_records(None)


def test_validate_records_rejects_empty_list():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    with pytest.raises(ValueError, match="Response data is empty"):
        validator.validate_records([])


def test_validate_records_rejects_invalid_record():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    with pytest.raises(
        ValueError,
        match="Response contains invalid record format"
    ):
        validator.validate_records(
            ["invalid record"]
        )


def test_to_dataframe_rejects_missing_required_column():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    records = [
        {
            "companyName": "Test Company",
            "price": 100
        }
    ]

    with pytest.raises(
        ValueError,
        match="Missing required columns"
    ):
        validator.to_dataframe(records)


def test_to_dataframe_removes_duplicate_records():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    records = [
        {
            "symbol": "ABC",
            "price": 100
        },
        {
            "symbol": "ABC",
            "price": 100
        },
        {
            "symbol": "XYZ",
            "price": 200
        }
    ]

    dataframe = validator.to_dataframe(records)

    assert len(dataframe) == 2
    assert dataframe["symbol"].tolist() == [
        "ABC",
        "XYZ"
    ]


def test_to_dataframe_creates_valid_dataframe():
    validator = DataValidator(
        required_columns=["symbol"]
    )

    records = [
        {
            "symbol": "ABC",
            "price": 100
        },
        {
            "symbol": "XYZ",
            "price": 200
        }
    ]

    dataframe = validator.to_dataframe(records)

    assert isinstance(dataframe, pd.DataFrame)
    assert not dataframe.empty
    assert "symbol" in dataframe.columns