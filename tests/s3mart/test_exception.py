

# imports - module imports
from s3mart.exception import (
    S3martError
)

# imports - test imports
import pytest

def test_s3mart_error():
    with pytest.raises(S3martError):
        raise S3martError