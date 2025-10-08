# Server-Side Request Forgery (SSRF)

## What is SSRF?
SSRF vulnerabilities occur when a server-side application makes HTTP or other network requests on behalf of user input without proper sanitization or validation.

## Attacker Goals

- Access internal services (metadata endpoints, databases, Redis)
- Perform port scans
- Bypass network restrictions
- Exploit internal APIs

## Common SSRF Sources

| Channel           | Example                           |
|-------------------|-----------------------------------|
| Image fetcher     | GET /proxy?url=http://...         |
| PDF generator     | Converts HTML with remote links   |
| Webhooks          | Attacker-controlled endpoints     |
| URL validation    | Insecure redirects, checks        |

## Example Payloads

```
http://127.0.0.1:3306
http://169.254.169.254/latest/meta-data/
http://localhost/admin
```

## Risk Impact

| Risk                  | Impact                          |
|------------------------|---------------------------------|
| Internal discovery     | Port scanning, host mapping     |
| Data leakage           | Read secrets, tokens            |
| RCE (via chained vuln) | Reach Gogs, Jenkins, etc.       |

## Mitigation

- Whitelist allowed destinations
- Block internal IP ranges
- Enforce DNS resolution restrictions
- Log outbound requests
- Use SSRF-aware libraries
