import pytest
from pydantic import ValidationError
from sst.contracts.error_model import ErrorModel

def test_error_model_valid():
    err = ErrorModel(type="RETRYABLE", message="Timeout")
    assert err.type == "RETRYABLE"
    assert err.message == "Timeout"
    assert err.retry_count == 0

def test_error_model_invalid_type():
    with pytest.raises(ValidationError):
        ErrorModel(type="INVALID_TYPE", message="Bad")
