import os

import pytest


@pytest.fixture
def setenv_orwynntest_should_drop_sql_to_1():
    os.environ["ORWYNNTEST_SHOULD_DROP_SQL"] = "1"
    yield
    del os.environ["ORWYNNTEST_SHOULD_DROP_SQL"]
