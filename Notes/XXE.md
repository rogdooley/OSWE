# XML External Entity (XXE) Injection

## What is XXE?
XXE occurs when an XML parser improperly processes external entities within user-supplied XML documents, allowing attackers to:

- Read arbitrary local files
- Perform SSRF-style attacks
- Trigger DoS via entity expansion ("billion laughs")

## Commonly Vulnerable APIs

| Language | Library/API                     |
|----------|----------------------------------|
| Java     | javax.xml.parsers.DocumentBuilder |
| .NET     | XmlDocument, XmlTextReader       |
| Python   | xml.dom.minidom, lxml             |
| PHP      | libxml, SimpleXML, DOMDocument   |

## Exploit Example

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

## Exploitable Channels

- SOAP-based web services
- XML file uploads
- SAML assertions
- REST APIs accepting XML POST bodies

## Risk Impact

| Risk                       | Impact                     |
|---------------------------|----------------------------|
| File disclosure           | Exfiltrate sensitive data  |
| SSRF                      | Target internal services   |
| DoS (expansion attacks)   | Crash XML parsers          |

## Mitigation

- Disable DTDs in XML parsers
- Use safe libraries or features (`defusedxml` in Python)
- Prefer JSON over XML when possible
- Apply schema validation if XML is required
