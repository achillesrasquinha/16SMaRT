

# imports - module imports
from geomeat.exception import (
    GeomeatError
)

# imports - test imports
import pytest

def test_geomeat_error():
    with pytest.raises(GeomeatError):
        raise GeomeatError