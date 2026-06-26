"""HTTP client abstraction for future scrapers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import json
from urllib import request

from scrapers.core.retry_policy import RetryPolicy
from scrapers.core.source_config import SourceConfig


@dataclass(frozen=True)
class HttpRequest:
    """Request data passed to a transport."""

    method: str
    url: str
    headers: dict[str, str]
    timeout: float
    body: bytes | None = None


@dataclass(frozen=True)
class HttpResponse:
    """Transport-independent HTTP response."""

    status_code: int
    text: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)


Transport = Callable[[HttpRequest], HttpResponse]


def urllib_transport(http_request: HttpRequest) -> HttpResponse:
    """Default urllib transport for future live scraper/backend use."""
    req = request.Request(
        http_request.url,
        data=http_request.body,
        headers=http_request.headers,
        method=http_request.method,
    )
    with request.urlopen(req, timeout=http_request.timeout) as response:  # noqa: S310 - opt-in transport.
        body = response.read().decode("utf-8", errors="replace")
        return HttpResponse(
            status_code=response.status,
            text=body,
            url=response.url,
            headers=dict(response.headers.items()),
        )


@dataclass(frozen=True)
class HttpClient:
    """Reusable HTTP abstraction with retries and custom headers."""

    config: SourceConfig = field(default_factory=SourceConfig)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    transport: Transport = urllib_transport

    def get(self, url: str, headers: Mapping[str, str] | None = None) -> HttpResponse:
        """Prepare and execute a GET request through the configured transport."""
        request_headers = {"User-Agent": self.config.user_agent}
        if headers:
            request_headers.update(headers)
        http_request = HttpRequest(
            method="GET",
            url=url,
            headers=request_headers,
            timeout=self.config.timeout,
        )
        return self.retry_policy.run(lambda: self.transport(http_request))  # type: ignore[return-value]

    def post_json(self, url: str, payload: Mapping[str, object], headers: Mapping[str, str] | None = None) -> HttpResponse:
        """Prepare and execute a JSON POST request through the configured transport."""
        request_headers = {"User-Agent": self.config.user_agent, "Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        http_request = HttpRequest(
            method="POST",
            url=url,
            headers=request_headers,
            timeout=self.config.timeout,
            body=json.dumps(payload).encode("utf-8"),
        )
        return self.retry_policy.run(lambda: self.transport(http_request))  # type: ignore[return-value]
