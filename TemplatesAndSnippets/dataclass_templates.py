from dataclasses import dataclass

@dataclass
class UserResult:
    id: int
    username: str

@dataclass
class RequestLog:
    url: str
    status_code: int
    timestamp: str  # e.g., ISO 8601

@dataclass
class HttpResponseData:
    headers: dict[str, str]
    body: str
    redirected: bool