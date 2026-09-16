import pytest
from app.etl.retry import retry_operation

def test_retry_operation_success():
    calls = 0
    def success_func():
        nonlocal calls
        calls += 1
        return "ok"

    result = retry_operation(success_func, max_retries=3, delay_seconds=0)
    assert result == "ok"
    assert calls == 1

def test_retry_operation_retries_and_succeeds():
    calls = 0
    def transient_fail():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ValueError("Temporary glitch")
        return "recovered"

    result = retry_operation(transient_fail, max_retries=3, delay_seconds=0)
    assert result == "recovered"
    assert calls == 2

def test_retry_operation_raises_last_exception():
    calls = 0
    def fail_always():
        nonlocal calls
        calls += 1
        raise ValueError("Persistent error")

    with pytest.raises(ValueError, match="Persistent error"):
        retry_operation(fail_always, max_retries=3, delay_seconds=0)
    assert calls == 3

def test_retry_operation_zero_retries():
    with pytest.raises(RuntimeError, match="failed after 0 attempts"):
        retry_operation(lambda: "ok", max_retries=0, delay_seconds=0)
