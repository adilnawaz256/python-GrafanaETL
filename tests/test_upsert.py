import pytest
from app.loaders.ran_loader import RANLoader

def test_ran_loader_upsert_metadata():
    assert RANLoader.table_name == "core_ran_kpi"
    assert RANLoader.conflict_columns == ["stime", "d1_plmn"]
    assert "cell_availability" in RANLoader.update_columns
    assert "erab_drop_rate" in RANLoader.update_columns
