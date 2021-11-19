

# imports - module imports
from s3mart.exception import (
    GeomeatError
)

# imports - test imports
import pytest

def test_s3mart_error():
    with pytest.raises(GeomeatError):
        raise GeomeatError