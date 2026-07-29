"""Unit tests for Phase 3 webhook receiver, HMAC validation, and delivery idempotency."""
import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from backend.core.config import get_settings
from backend.core.exceptions import SecurityError
from backend.main import app
from backend.webhook_receiver.parser import parse_github_pull_request_event
from backend.webhook_receiver.validator import verify_github_signature

client = TestClient(app)
settings = get_settings()


def _compute_hmac(body: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def test_hmac_signature_validation_success() -> None:
    payload = b'{"action": "opened"}'
    sig = _compute_hmac(payload, settings.GITHUB_WEBHOOK_SECRET)
    assert verify_github_signature(payload, sig, settings.GITHUB_WEBHOOK_SECRET) is True


def test_hmac_signature_validation_failure() -> None:
    payload = b'{"action": "opened"}'
    with pytest.raises(SecurityError):
        verify_github_signature(payload, "sha256=invalid_signature", settings.GITHUB_WEBHOOK_SECRET)


def test_webhook_parser_supported_event() -> None:
    payload = {
        "action": "opened",
        "number": 42,
        "pull_request": {"number": 42, "head": {"sha": "abcdef123456"}},
        "repository": {"full_name": "owner/test-repo"},
    }
    event = parse_github_pull_request_event("pull_request", "deliv-101", payload)
    assert event is not None
    assert event.pr_number == 42
    assert event.repository == "owner/test-repo"


def test_webhook_endpoint_success() -> None:
    payload_dict = {
        "action": "opened",
        "number": 100,
        "pull_request": {"number": 100, "head": {"sha": "sha123"}},
        "repository": {"full_name": "owner/repo"},
    }
    body_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = _compute_hmac(body_bytes, settings.GITHUB_WEBHOOK_SECRET)

    response = client.post(
        "/webhook/github",
        content=body_bytes,
        headers={
            "X-GitHub-Delivery": "unique-delivery-001",
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": sig,
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["delivery_id"] == "unique-delivery-001"


def test_webhook_endpoint_idempotency_duplicate_delivery() -> None:
    payload_dict = {
        "action": "opened",
        "number": 101,
        "pull_request": {"number": 101, "head": {"sha": "sha123"}},
        "repository": {"full_name": "owner/repo"},
    }
    body_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = _compute_hmac(body_bytes, settings.GITHUB_WEBHOOK_SECRET)

    headers = {
        "X-GitHub-Delivery": "dup-delivery-999",
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json",
    }

    # First request -> Queued
    res1 = client.post("/webhook/github", content=body_bytes, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "queued"

    # Second request with same delivery ID -> Acknowledged duplicate
    res2 = client.post("/webhook/github", content=body_bytes, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "acknowledged"
    assert "Duplicate delivery ignored" in res2.json()["message"]
