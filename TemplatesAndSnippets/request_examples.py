import requests

def simple_get(url: str) -> requests.Response:
    return requests.get(url)

def get_no_redirect(url: str) -> requests.Response:
    return requests.get(url, allow_redirects=False)

def post_form_data(url: str, data: dict) -> requests.Response:
    return requests.post(url, data=data)

def post_json(url: str, json_payload: dict) -> requests.Response:
    return requests.post(url, json=json_payload)

def get_with_headers(url: str, headers: dict) -> requests.Response:
    return requests.get(url, headers=headers)

def session_with_cookies(base_url: str, login_data: dict) -> requests.Session:
    s = requests.Session()
    s.post(f"{base_url}/login", data=login_data)
    return s