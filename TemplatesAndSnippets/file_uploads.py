"""
Upload Templates with `requests`

This module contains reusable snippets for uploading files, JSON, raw binary data,
multipart forms, and debugging uploads using the `requests` module.
"""

import requests
import json
from typing import Any

# Configuration
URL = "https://example.com/upload"
PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def upload_urlencoded(data: dict[str, str]) -> requests.Response:
    return requests.post(URL, data=data)


def upload_json(json_data: dict[str, Any]) -> requests.Response:
    return requests.post(URL, json=json_data)


def upload_file(file_path: str) -> requests.Response:
    with open(file_path, "rb") as f:
        return requests.post(URL, files={"file": f})


def upload_file_with_form(
    file_path: str, form_data: dict[str, str]
) -> requests.Response:
    with open(file_path, "rb") as f:
        return requests.post(URL, files={"file": f}, data=form_data)


def upload_arbitrary_binary(data: bytes) -> requests.Response:
    headers = {"Content-Type": "application/octet-stream"}
    return requests.post(URL, data=data, headers=headers)


def upload_multipart_json_and_file(
    file_path: str, json_payload: dict[str, Any]
) -> requests.Response:
    from requests_toolbelt.multipart.encoder import MultipartEncoder

    m = MultipartEncoder(
        fields={
            "metadata": ("", json.dumps(json_payload), "application/json"),
            "file": ("upload.bin", open(file_path, "rb"), "application/octet-stream"),
        }
    )
    headers = {"Content-Type": m.content_type}
    return requests.post(URL, data=m, headers=headers)


def debug_request(r: requests.Response) -> None:
    print("Status Code:", r.status_code)
    print("Response Headers:", r.headers)
    print("Response Text:", r.text)
    print("Request Body:", r.request.body)
    print("Request Headers:", r.request.headers)
    print("Request URL:", r.request.url)
