"""Test SSRF Protection and URL validation."""

import pytest
from apps.api.app.core.ssrf import validate_url_safety
from apps.api.app.core.exceptions import URLFetchError


def test_ssrf_rejects_localhost():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("http://localhost:8000/secret")
    assert "private/internal" in str(exc.value) or "forbidden" in str(exc.value)


def test_ssrf_rejects_127_0_0_1():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("http://127.0.0.1:5000/admin")
    assert "forbidden" in str(exc.value) or "blocked" in str(exc.value)


def test_ssrf_rejects_cloud_metadata():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("http://169.254.169.254/latest/meta-data/")
    assert "metadata" in str(exc.value) or "forbidden" in str(exc.value)


def test_ssrf_rejects_private_rf1918():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("http://192.168.1.1/router")
    assert "forbidden" in str(exc.value)


def test_ssrf_rejects_non_http_protocol():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("file:///etc/passwd")
    assert "protocol" in str(exc.value)

    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("ftp://example.com/file")
    assert "protocol" in str(exc.value)


def test_ssrf_rejects_non_standard_ports():
    with pytest.raises(URLFetchError) as exc:
        validate_url_safety("http://example.com:22/admin")
    assert "port" in str(exc.value).lower()
