import re
import pandas as pd
import pytest

from backend.sheets import list_client_tabs, fetch_planned_hours


def test_list_client_tabs_includes_glencor_golf_and_excludes_metadata():
    tabs = list_client_tabs()
    # Glencor Golf should be present
    assert 'Glencor Golf' in tabs
    # Metadata (Client Tasks List Notes) should be excluded
    assert 'Client Tasks List Notes' not in tabs
    # Month-year tabs like 'May - 2025' should be excluded
    assert all(not re.match(r'^[A-Za-z]+ - \d{4}$', t) for t in tabs)


@pytest.mark.parametrize("start,end", [
    ("2025-05-01", "2025-05-31"),
    ("2025-06-01", "2025-06-30"),
])
def test_fetch_planned_hours_filters_by_date_glencor(start, end):
    df = fetch_planned_hours(start, end, 'Glencor Golf')

    # Should be a DataFrame with Date and Hours columns
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"Date", "Hours"}

    # If there's data, it should be within the requested window and hours numeric
    if not df.empty:
        assert df['Date'].min() >= pd.to_datetime(start)
        assert df['Date'].max() <= pd.to_datetime(end)
        assert pd.api.types.is_numeric_dtype(df['Hours'])
    else:
        # No data is acceptable
        assert df.empty
