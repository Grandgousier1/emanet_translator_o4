import pytest
from src.offline.pipeline_offline import run_offline

@pytest.mark.skip(reason='Network download required for real test')
def test_pipeline_stub():
    assert True
